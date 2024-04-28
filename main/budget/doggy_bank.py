from terminology import in_red

from main.constants.sheet_id import DOGGY_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

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
                    print(in_red(f"\n\n!!!!!! YOU OWE {owed} TO THE DOGGY BANK !!!!!!").in_bold())
            except ValueError:
                pass
            return

    print("Name not found in sheet:", NAME)
