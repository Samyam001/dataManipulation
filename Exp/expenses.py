#!/usr/bin/env python3
"""
Expense Calculator
-------------------
Paste a bank/credit-card statement copied from an email into a text file
(default: statement.txt), and this script will:

  1. Extract individual transactions (date, description, amount)
  2. Categorize each transaction (Food, Shopping, Bills, Transport, etc.)
  3. Print a summary report: totals by category, top expenses, and grand total

USAGE:
  python3 expense_calculator.py statement.txt
  (if no filename given, it looks for "statement.txt" in the current folder)

HOW TO GET YOUR STATEMENT TEXT:
  Open the email/statement, select all the transaction text, copy it,
  and paste it into a plain .txt file. The parser is flexible about
  formatting - it looks for lines containing a date and a dollar amount.
"""

import re
import sys
from collections import defaultdict
from datetime import datetime


# ----------------------------------------------------------------------
# 1. CATEGORY RULES - add/edit keywords to match your own spending habits
# ----------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Food & Dining": [
        "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "kfc",
        "pizza", "food", "eatery", "diner", "bakery", "bar", "grill",
        "doordash", "ubereats", "grubhub", "swiggy", "zomato"
    ],
    "Groceries": [
        "grocery", "supermarket", "walmart", "costco", "kroger", "aldi",
        "whole foods", "trader joe", "mart", "bazaar"
    ],
    "Transport": [
        "uber", "lyft", "taxi", "gas station", "shell", "chevron", "fuel",
        "parking", "metro", "transit", "train", "airline", "flight"
    ],
    "Shopping": [
        "amazon", "ebay", "target", "best buy", "shopping", "store",
        "mall", "clothing", "apparel", "shoes"
    ],
    "Bills & Utilities": [
        "electric", "water bill", "internet", "phone bill", "utility",
        "insurance", "rent", "mortgage", "verizon", "at&t", "comcast",
        "subscription", "netflix", "spotify", "hulu"
    ],
    "Health": [
        "pharmacy", "doctor", "hospital", "clinic", "dental", "cvs",
        "walgreens", "medical", "health"
    ],
    "Entertainment": [
        "movie", "cinema", "theatre", "concert", "game", "steam",
        "playstation", "xbox"
    ],
    "Transfers & Withdrawals": [
        "atm", "withdrawal", "transfer", "cash advance", "zelle", "venmo"
    ],
}

DATE_PATTERN = re.compile(
    r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4})"
)

# Matches amounts like: $1,234.56  -1234.56  1234.56  1,234.56  (1234.56)
AMOUNT_PATTERN = re.compile(
    r"[-(]?\$?\s?-?\d{1,3}(?:,\d{3})*(?:\.\d{2})\)?"
)


def parse_amount(raw: str) -> float:
    """Convert a matched amount string into a float (negative = debit)."""
    negative = "(" in raw or raw.strip().startswith("-")
    cleaned = re.sub(r"[^\d.]", "", raw)
    if not cleaned:
        return 0.0
    value = float(cleaned)
    return -value if negative else value


def parse_statement(text: str):
    """
    Scan each line of the statement text and pull out transactions.
    Returns a list of dicts: {date, description, amount}
    """
    transactions = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        date_match = DATE_PATTERN.search(line)
        amount_matches = AMOUNT_PATTERN.findall(line)

        if not amount_matches:
            continue  # no dollar amount on this line, skip it

        # Use the LAST amount on the line (statements usually put the
        # transaction amount at the end, with balance sometimes after it)
        amount_raw = amount_matches[-1]
        amount = parse_amount(amount_raw)

        if amount == 0.0:
            continue

        date_str = date_match.group(0) if date_match else "Unknown"

        # Description = whatever's left after removing the date and amount
        description = line
        if date_match:
            description = description.replace(date_match.group(0), "")
        description = description.replace(amount_raw, "")
        description = re.sub(r"\s{2,}", " ", description).strip(" -|,\t")

        if not description:
            description = "Unknown transaction"

        transactions.append({
            "date": date_str,
            "description": description,
            "amount": amount,
        })

    return transactions


def categorize(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return "Uncategorized"


def build_report(transactions):
    by_category = defaultdict(list)
    total_spent = 0.0
    total_income = 0.0

    for tx in transactions:
        category = categorize(tx["description"])
        tx["category"] = category
        by_category[category].append(tx)

        if tx["amount"] < 0:
            total_spent += -tx["amount"]
        else:
            total_income += tx["amount"]

    return by_category, total_spent, total_income


def print_report(transactions):
    if not transactions:
        print("No transactions were found. Check that your statement.txt")
        print("file contains lines with both a date and a dollar amount.")
        return

    by_category, total_spent, total_income = build_report(transactions)

    print("=" * 60)
    print("EXPENSE REPORT")
    print("=" * 60)

    print(f"\nTotal transactions found: {len(transactions)}")
    print(f"Total spent (debits):     ${total_spent:,.2f}")
    print(f"Total received (credits): ${total_income:,.2f}")
    print(f"Net:                      ${total_income - total_spent:,.2f}")

    print("\n" + "-" * 60)
    print("SPENDING BY CATEGORY")
    print("-" * 60)

    # Sort categories by total spend, highest first
    category_totals = {
        cat: sum(-tx["amount"] for tx in txs if tx["amount"] < 0)
        for cat, txs in by_category.items()
    }
    for cat, total in sorted(category_totals.items(), key=lambda x: -x[1]):
        if total <= 0:
            continue
        pct = (total / total_spent * 100) if total_spent else 0
        print(f"  {cat:<25} ${total:>10,.2f}   ({pct:5.1f}%)")

    print("\n" + "-" * 60)
    print("TOP 10 EXPENSES")
    print("-" * 60)
    expenses = [tx for tx in transactions if tx["amount"] < 0]
    expenses.sort(key=lambda tx: tx["amount"])
    for tx in expenses[:10]:
        print(f"  {tx['date']:<12} {tx['description'][:35]:<35} "
              f"${-tx['amount']:>9,.2f}   [{tx['category']}]")

    print("\n" + "-" * 60)
    print("ALL TRANSACTIONS")
    print("-" * 60)
    for tx in transactions:
        sign = "-" if tx["amount"] < 0 else "+"
        print(f"  {tx['date']:<12} {tx['description'][:35]:<35} "
              f"{sign}${abs(tx['amount']):>9,.2f}   [{tx['category']}]")

    print("\n" + "=" * 60)


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "statement.txt"

    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Could not find '{filename}'.")
        print("Paste your statement text into a file with that name, "
              "or run: python3 expense_calculator.py <your_file.txt>")
        return

    transactions = parse_statement(text)
    print_report(transactions)


if __name__ == "__main__":
    main()