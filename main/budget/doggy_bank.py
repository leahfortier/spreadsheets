from main.constants.sheet_id import DOGGY_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data
from util.warn import warn

SPREADSHEET_ID = DOGGY_ID
OWED_TAB = "Total"

NAME = "Leah"


def check_doggy_bank():
    sheet: Sheet = Sheet(get_sheet_data(DOGGY_ID, OWED_TAB))
    for row in sheet.rows:
        if NAME in sheet.get(row, "Provider"):
            owed = sheet.get(row, "Owe")
            try:
                if float(owed.lstrip("$")) > 0:
                    warn(f"\n\n!!!!!! YOU OWE {owed} TO THE DOGGY BANK !!!!!!")
            except ValueError:
                pass
            return

    print("Name not found in sheet:", NAME)
