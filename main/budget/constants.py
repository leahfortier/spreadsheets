from datetime import datetime
from pathlib import Path

from main.constants.sheet_id import BUDGET_ID

TRANSACTIONS_FILE = str(Path.home() / "Downloads/transactions.csv")

YEAR = 2024

SPREADSHEET_ID = BUDGET_ID
TRANSACTIONS_TAB = f'{YEAR} Transactions'

CATEGORY = "Category"
MONTH = "Month"
DATE = "Date"
AMOUNT = "Amount"
TRANSACTION_TYPE = "Transaction Type"
ORIGINAL_DESCRIPTION = "Original Description"
DESCRIPTION = "Description"
LABELS = "Labels"

KEY_FIELDS = [DATE, ORIGINAL_DESCRIPTION, AMOUNT, TRANSACTION_TYPE]

POSITIVE_TRANSACTION = "credit"
NEGATIVE_TRANSACTION = "debit"

DATE_FORMAT = "%m/%d/%Y"
MONTH_FORMAT = "'%B %Y"

START_DATE = datetime(year=YEAR, month=1, day=1)
