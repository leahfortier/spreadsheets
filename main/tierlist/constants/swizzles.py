from typing import List

from main.constants.sheet_id import L_SWIZZLE_ID
from constants.sheets import TierSheet
from util.data import Sheet
from util.general import remove_suffix
from util.sheets_formulas import column_range


RATING_FIELD = "Rating"
TITLE_FIELD = "Title"
ERA_FIELD = "Era"


# Manual ratings -- +2 because not zero-indexed and ignore schema row
def update_swizzle(sheet: Sheet, index: int, row: List[str]) -> None:
    era = remove_suffix(sheet.get(row, ERA_FIELD), [" (TV)"])
    era_tab = f'Era - {era}'
    era_title_col = "A"
    era_rating_col = "C"

    main_title_row = f'{sheet.column(TITLE_FIELD)}{index + 2}'
    era_title_range = column_range(era_title_col, tab=era_tab, fixed=True)
    era_rating_range = column_range(era_rating_col, tab=era_tab, fixed=True)

    # Ex: =FILTER('Era - Folklore'!C$2:C, D3='Era - Folklore'!A$2:A)
    rating_formula = f"=FILTER({era_rating_range}, {main_title_row}={era_title_range})"
    sheet.update(row, RATING_FIELD, rating_formula, print_diff=False)


SWIZZLES: TierSheet = TierSheet(
    spreadsheet_id=L_SWIZZLE_ID,
    id_fields=["Sort"],
    tiers_tab="Notes",
    tiers_field="Ratings",
    sort_tab="Discography",
    rating_field=RATING_FIELD,
    new_rank_field="Rank",
    old_rank_field="Old",
    diff_field="+/-",
    on_update=update_swizzle,
)
