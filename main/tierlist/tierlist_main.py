from constants.sheets import SWIZZLES
from tierlist import sort_tiers
from main.constants.sheet_id import L_SWIZZLE_ID, MEL_SWIZZLE_ID


def main():
    SWIZZLES.spreadsheet_id = L_SWIZZLE_ID
    SWIZZLES.spreadsheet_id = MEL_SWIZZLE_ID
    sort_tiers(SWIZZLES)


main()
