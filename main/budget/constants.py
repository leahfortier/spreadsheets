from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from main.constants.sheet_id import BUDGET_ID
from main.util.file_io import from_csv
from util.data import Sheet
from util.sheets_parse import get_sheet_data

YEAR = 2026

SPREADSHEET_ID = BUDGET_ID
TRANSACTIONS_TAB = f'{YEAR} Transactions'


# "Date","Description","Amount (in $)","Account Name","Transaction Type","Category","Subcategory","Hidden Transaction"
class TransactionFields(str, Enum):
    CATEGORY = "Category"
    MONTH = "Month"
    DATE = "Date"
    AMOUNT = "Amount (in $)"
    ACCOUNT_NAME = "Account Name"
    DESCRIPTION = "Description"
    LABELS = "Labels"


KEY_FIELDS: List[TransactionFields] = [
    TransactionFields.DATE,
    TransactionFields.DESCRIPTION,
    TransactionFields.AMOUNT,
    TransactionFields.ACCOUNT_NAME
]

FIDELITY_DATE_FORMAT = "%b-%d-%Y"
DATE_FORMAT = "%m-%d-%Y"

START_DATE = datetime(year=YEAR, month=1, day=1)

TRANSACTIONS_HOME_PATH: str = "Downloads/"
TRANSACTIONS_PATTERN: str = "Transactions_*"


# Fidelity exports transactions to the format 'Transactions_<timestamp>'
#   - Ex: 'Transactions_Apr-04-2026 at 5.27.05 PM'
# Return the contents of the most recent file that matches that pattern
def transactions_file() -> List[List[str]]:
    folder_path = Path.home() / TRANSACTIONS_HOME_PATH
    files = list(folder_path.glob(TRANSACTIONS_PATTERN))

    if not files:
        raise FileNotFoundError(f"No files found in {TRANSACTIONS_HOME_PATH} with pattern '{TRANSACTIONS_PATTERN}'.")

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    file_path = str(latest_file.resolve())
    print("Transaction file found:", file_path)

    return from_csv(file_path)


# Returns sheet data for downloaded transactions file
# Transaction file format (we only care about schema and transaction rows):
#      Spending Transactions:
#      <schema row>
#      <transaction rows>
#
#      DATA GLOSSARY:
#      <schema descriptions>
#
#      <other information sections I don't care about>
def get_new_transactions() -> Sheet:
    rows = transactions_file()

    empty_index = next((i for i, row in enumerate(rows) if not row))

    sheet = Sheet(
        rows[1:empty_index],
        id_fields=KEY_FIELDS,
        allow_duplicate_keys=True
    )

    for row in sheet.rows:
        # Convert date to same format
        date_field = sheet.get(row, TransactionFields.DATE)
        date_value = datetime.strptime(date_field, FIDELITY_DATE_FORMAT)
        formatted_date = date_value.strftime(DATE_FORMAT)
        sheet.set(row, TransactionFields.DATE, formatted_date)

        # Convert amount to two decimals
        amount_value = float(sheet.get(row, TransactionFields.AMOUNT))
        formatted_amount = f"{amount_value:.2f}"
        sheet.set(row, TransactionFields.AMOUNT, formatted_amount)

        # Remove category
        sheet.set(row, TransactionFields.CATEGORY, '')

    sheet.reset_ids()

    return sheet


# Returns sheet data for transactions currently in the spreadsheet
def get_current_transactions() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, TRANSACTIONS_TAB),
        auto_fields=[TransactionFields.MONTH],
        id_fields=KEY_FIELDS,
        schema_size=2,
        allow_duplicate_keys=True
    )
