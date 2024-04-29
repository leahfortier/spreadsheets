from constants.swizzles import SWIZZLES
from tierlist import sort_tiers, sort_column
from main.constants.sheet_id import L_SWIZZLE_ID, MEL_SWIZZLE_ID
from constants.genshin import GENSHIN


def main():
    SWIZZLES.spreadsheet_id = L_SWIZZLE_ID
    SWIZZLES.spreadsheet_id = MEL_SWIZZLE_ID
    sort_tiers(SWIZZLES)

    sort_column(GENSHIN)


main()
