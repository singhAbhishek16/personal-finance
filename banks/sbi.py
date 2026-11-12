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
    # (SBI CSV strings deta hai: "01 July 2026", "1,234.00" -- isey typed banana padta hai)
    data["date"] = pd.to_datetime(data["date"], format="%d %B %Y")
    for col in ("debit", "credit"):
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
    return data
