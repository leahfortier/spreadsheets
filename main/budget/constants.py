from datetime import datetime
from pathlib import Path
from typing import List

from main.constants.sheet_id import BUDGET_ID
from main.util.file_io import from_csv
from main.util.time import date_str

YEAR = 2024

SPREADSHEET_ID = BUDGET_ID
TRANSACTIONS_TAB = f'{YEAR} Transactions'

# Fields: "Date","Description","Institution","Account","Category","Is Hidden","Is Pending","Amount"
CATEGORY = "Category"
MONTH = "Month"
DATE = "Date"
AMOUNT = "Amount"
ACCOUNT_NAME = "Account"
INSTITUTION = "Institution"
DESCRIPTION = "Description"
LABELS = "Labels"

KEY_FIELDS = [DATE, DESCRIPTION, AMOUNT, ACCOUNT_NAME, INSTITUTION]

DATE_FORMAT = "%m/%d/%Y"
MONTH_FORMAT = "'%B %Y"

START_DATE = datetime(year=YEAR, month=1, day=1)

TRANSACTIONS_HOME_PATH: str = "Downloads/"
CHECK_DAYS = 7


# Fidelity exports transactions to the format transactions_%Y_%m_%d.csv
# Return the contents of the most recent file that matches that pattern
def transactions_file() -> List[List[str]]:
    for delta in range(0, CHECK_DAYS):
        date_suffix = date_str(-delta, "%Y_%m_%d")
        file_path = str(Path.home() / TRANSACTIONS_HOME_PATH / f"transactions_{date_suffix}.csv")
        try:
            return from_csv(file_path)
        except FileNotFoundError:
            continue

    raise FileNotFoundError(f"No file found for the last {CHECK_DAYS} days")
