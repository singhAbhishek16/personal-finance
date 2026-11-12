"""ICICI PDF statement -> normalized transactions.

Contract: parse() returns a DataFrame with columns -> date, debit, credit, description.

Poora ICICI PDF parsing yahीn hota hai (self-contained). pdf_plumber.py ek
alag standalone testing sandbox hai -- wo is file ko reference nahi karta.

Why not pdfplumber.extract_tables()?  The statement has no real table grid --
the ruling lines are noisy and inconsistent.  The data is positional text: each
transaction is a *block* of several visual lines:

    Aishwarya                                   <- payee name        (x~192)
    1  01.06.2026          115.00   414543.52   <- ANCHOR row
    UPI/Aishwarya/paytmqr.../grocery/YES BANK   <- remarks, wrapped
    L/774346105140/IBL9a348abe...               <- remarks cont.

So we parse by word coordinates instead: group words into visual lines, treat the
"S.No + DD.MM.YYYY" line as the spine of each transaction, attach the payee line
above and the wrapped remarks lines below, and classify the amount as Withdrawal
or Deposit by its x-position (column boundaries derived from the page header).
"""

import re

import pandas as pd
import pdfplumber

# ANCHOR_RE "s.no + date" pattern ka regex match karta hai. boleto, pdf se wo line choose karne ko jo transaction hai; aur baki ignore
ANCHOR_RE = re.compile(r"^\s*(\d+)\s+(\d{2}\.\d{2}\.\d{4})\b")
# A monetary value, e.g. "1,234.56" or "115.00".
AMOUNT_RE = re.compile(r"^[\d,]*\d\.\d{2}$")

COLUMNS = [
    "S No.", "Date", "Cheque Number", "Payee",
    "Remarks", "Withdrawal", "Deposit", "Balance",
]

# shared "contract" har bank module ko ye 4 columns return karne hai
CONTRACT_COLUMNS = ["date", "debit", "credit", "description"]


def group_into_lines(words, tol=3):
    """jin bhi words ka top se distance same hai, wo same row hai"""
    lines = {}
    #TODO: next() kaise kaam karta hai; samajhna isey
    for w in words:
        key = next((k for k in lines if abs(k - w["top"]) <= tol), w["top"])
        lines.setdefault(key, []).append(w)
    return [sorted(lines[k], key=lambda w: w["x0"]) for k in sorted(lines)]


def header_separators(pdf):
    """apne pdf me 3 column hai - withdrawl, deposit, balance
    maloom kaise chalega, kaun si value kis column ki hai? iske liye ye function column wali
    line ka coordinate return karta hai.
    sample output: withdrawl_seprator: 473.79; deposit_separator: 532.14
    boleto Withdrawl|Deposit aur Deposit|Balance wale column lines ka coordinate
    phir aise decide karte hai -
    1. agar number withdrawl_seprator coordinate ke left me hai - withdraw ki value hai
    2. number withdrawl aur deposit_seprator coordinates ke beech me hai - deposit hai
    3. aur agar deposit coordinate ke right me hai - balance hai
    """
    for page in pdf.pages:
        hdr = {w["text"]: w["x0"] for w in page.extract_words()
               if w["text"] in ("Withdrawal", "Deposit", "Balance")}
        if {"Withdrawal", "Deposit", "Balance"} <= hdr.keys():
            return hdr["Deposit"], hdr["Balance"]  # withdrawl_separator, deposit_separator
    raise ValueError("Could not locate the transaction table header in the PDF.")


def to_float(text):
    return float(text.replace(",", ""))


def parse_anchor(line, withdrawl_seprator_coordinate, deposit_seprator_coordinate):
    """Parse a spine line into its fields. Returns a dict for the new transaction.

    The rightmost monetary value is always the running Balance; the other (if any)
    is the transaction amount, classified Withdrawal vs Deposit by its x0 against
    the header-derived separators.
    """
    text = " ".join(w["text"] for w in line)
    sno, date = ANCHOR_RE.match(text).groups()

    nums = [w for w in line if AMOUNT_RE.match(w["text"])]
    balance = to_float(nums[-1]["text"]) if nums else None

    withdrawal = deposit = None
    if len(nums) >= 2:
        amt = nums[-2]
        if amt["x1"] < withdrawl_seprator_coordinate:
            withdrawal = to_float(amt["text"])
        elif amt["x1"] < deposit_seprator_coordinate:
            deposit = to_float(amt["text"])
        else:  # same column as balance -> shouldn't happen; keep as withdrawal
            withdrawal = to_float(amt["text"])

    # Cheque number, if present, sits between the date and the remarks column.
    cheque = next(
        (w["text"] for w in line
         if 100 < w["x0"] < 180 and not AMOUNT_RE.match(w["text"])),
        None,
    )

    return {
        "S No.": int(sno),
        "Date": date,
        "Cheque Number": cheque,
        "Payee": None,
        "Remarks": [],
        "Withdrawal": withdrawal,
        "Deposit": deposit,
        "Balance": balance,
    }


def _extract_full(pdf_source):
    """Full parse: saare internal columns (Balance, S No. etc) ke saath.
    pdf_source path (str) ya file-like object dono ho sakta hai -- streamlit
    uploader file-like deta hai, aur pdfplumber.open() dono accept karta hai."""
    with pdfplumber.open(pdf_source) as pdf:
        withdrawl_seprator_coordinate, deposit_seprator_coordinate = header_separators(pdf)

        records = []
        pending_payee = None  # the non-anchor line seen just before an anchor

        for page in pdf.pages:
            for line in group_into_lines(page.extract_words()):
                """
                output of page.extract_words() look like:
                {'text': 'Transaction', 'x0': 60.24, 'x1': 107.76, 'top': 84.0, 'doctop': 5978.0, 'bottom': 92.0, 'upright': True, 'height': 8.0, 'width': 47.52, 'direction': 'ltr'}
                'transaction' word ka coordinate utha kar dera. top se kitna distance hai, left se kitna, etc
                last me jin saare words ka top se distance same hua, wo ek he row hai - brilliant way to create table when table is not there
                """
                text = " ".join(w["text"] for w in line).strip()

                if ANCHOR_RE.match(text):
                    txn = parse_anchor(line, withdrawl_seprator_coordinate, deposit_seprator_coordinate)
                    # sample txn output: txn: {'S No.': 1, 'Date': '01.07.2026', 'Cheque Number': None, 'Payee': None, 'Remarks': [], 'Withdrawal': 25000.0, 'Deposit': None, 'Balance': 519869.83}
                    txn["Payee"] = pending_payee
                    records.append(txn)
                    pending_payee = None
                    continue

                # Non-anchor text in the remarks column (x~192).
                if line and line[0]["x0"] >= 180:
                    if records and records[-1]["Balance"] is not None:
                        # Belongs to the current transaction's wrapped remarks.
                        records[-1]["Remarks"].append(text)
                    # Remember it as a possible payee for the next anchor.
                    pending_payee = text
                else:
                    pending_payee = None  # headers/footers reset the candidate

    for r in records:
        r["Remarks"] = " ".join(r["Remarks"])

    df = pd.DataFrame(records, columns=COLUMNS)
    df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
    return df


def to_contract(df):
    """Fully-parsed statement ko shared bank contract me map karta hai:
    date, debit (withdrawal = paisa gaya), credit (deposit = paisa aaya), description.
    jo side use nahi hui wo NaN rehti hai."""
    return pd.DataFrame({
        "date": df["Date"],
        "debit": df["Withdrawal"],
        "credit": df["Deposit"],
        "description": df["Remarks"],
    })


def validate(df):
    """Cross-check the running balance to catch any mis-parsed amount/column.
    (testing/debugging ke liye helper)"""
    bal = df["Balance"].to_numpy()
    wd = df["Withdrawal"].fillna(0).to_numpy()
    dp = df["Deposit"].fillna(0).to_numpy()
    issues = 0
    for i in range(1, len(df)):
        expected = bal[i - 1] - wd[i] + dp[i]
        if abs(expected - bal[i]) > 0.01:
            issues += 1
            print(f"  ! row {i} (S.No {df['S No.'][i]}): balance {bal[i]:.2f} "
                  f"!= expected {expected:.2f}")
    print(f"Balance check: {len(df) - 1 - issues}/{len(df) - 1} consecutive rows consistent.")


def parse(uploaded_file):
    """Public entrypoint (main app isey use karta hai): ICICI PDF padho aur
    contract-shaped DataFrame return karo -- columns: date, debit, credit, description.
    uploaded_file streamlit uploader ka file-like object hai (ya koi bhi path)."""
    return to_contract(_extract_full(uploaded_file))
