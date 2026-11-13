"""SBI CSV statement -> normalized transactions.

Contract: parse() returns a DataFrame with columns -> date, debit, credit, description.
(Ye logic pehle mymainstreamlit_refactored.py ke user_statement() me tha.)
"""

import pandas as pd

# SBI CSV ke apne column naam -> hamare shared contract naam
RENAME = {
    "Txn Date": "date",
    "Description": "description",
    "Debit": "debit",
    "Credit": "credit",
}


def parse(uploaded_file):
    """SBI CSV padho aur contract-shaped DataFrame return karo."""
    data = pd.read_csv(uploaded_file)
    data = data.rename(columns=RENAME)
    # sirf contract wale 4 columns rakho; baaki (Balance, Value Date, Ref No.) drop ho jaate hai
    data = data[["date", "debit", "credit", "description"]]

    # contract types: date -> datetime, debit/credit -> float (khaali side = NaN)
    # (SBI CSV strings deta hai: "1 Mar 2025", "1,234.00" -- isey typed banana padta hai)
    data["date"] = pd.to_datetime(data["date"], format="%d %b %Y")
    for col in ("debit", "credit"):
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )

    # shop + comment description se nikaalo (SBI ka apna format):
    # "TO TRANSFER-UPI/DR/<ref>/<SHOP>/<BANK>/<vpa>/<comment>"
    # -> shop = parts[3], comment = parts[-1]. jin rows me '/' structure nahi (e.g. credit), "" rakho
    parts = data["description"].astype(str).str.split("/")
    data["shop"] = parts.apply(lambda p: p[3].strip().lower() if len(p) > 3 else "")
    data["comment"] = parts.apply(lambda p: p[-1].strip().lower() if p else "")

    return data[["date", "debit", "credit", "description", "shop", "comment"]]
