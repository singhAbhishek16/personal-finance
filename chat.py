import os
import requests
import streamlit as st
from datetime import date, timedelta

BASE = "https://budget.abhishekprojects.com"
TOKEN=os.environ["FIREFLY_TOKEN"]
headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}

GROCERY_ID = 13
UNTRACKABLE_ID = 12


def sum_amount(path, start, end):
    total = 0.0
    params = {"start": start, "end": end, "limit": 50, "page": 1}
    while True:
        r = requests.get(f"{BASE}{path}", headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        for item in data["data"]:
            for split in item["attributes"]["transactions"]:
                total += float(split["amount"])
        pagination = data["meta"]["pagination"]
        if pagination["current_page"] >= pagination["total_pages"]:
            break
        params["page"] += 1
    return total


def sum_by_month(path, start, end):
    monthly = {}
    params = {"start": start, "end": end, "limit": 50, "page": 1}
    while True:
        r = requests.get(f"{BASE}{path}", headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        for item in data["data"]:
            for split in item["attributes"]["transactions"]:
                month = split["date"][:7]
                monthly[month] = monthly.get(month, 0.0) + float(split["amount"])
        pagination = data["meta"]["pagination"]
        if pagination["current_page"] >= pagination["total_pages"]:
            break
        params["page"] += 1
    return monthly


def last_3_months():
    first_of_current = date.today().replace(day=1)
    end = first_of_current - timedelta(days=1)  # last day of previous month
    start = first_of_current
    for _ in range(3):
        start = (start - timedelta(days=1)).replace(day=1)
    return start.isoformat(), end.isoformat()


st.title("Firefly III queries")

if st.button("1. How much amount did go in luxuries in October 2026?"):
    total = sum_amount("/api/v1/tags/luxury/transactions", "2026-10-01", "2026-10-31")
    st.write(total)

if st.button("2. What is total amount of grocery bills in last 3 months?"):
    start, end = last_3_months()
    monthly = sum_by_month(f"/api/v1/categories/{GROCERY_ID}/transactions", start, end)
    st.line_chart(
        {"month": sorted(monthly), "amount": [monthly[m] for m in sorted(monthly)]},
        x="month",
        y="amount",
    )

if st.button("3. How much amount has been going 'untrackable' in last 3 months?"):
    start, end = last_3_months()
    monthly = sum_by_month(f"/api/v1/categories/{UNTRACKABLE_ID}/transactions", start, end)
    st.line_chart(
        {"month": sorted(monthly), "amount": [monthly[m] for m in sorted(monthly)]},
        x="month",
        y="amount",
    )
