from typing import List, Callable

from main.constants.sheet_id import SWIZZLE_ID
from util.data import Sheet
from util.general import remove_suffix
from util.sheets_formulas import column_range


class TierSheet:
    def __init__(
            self,
            spreadsheet_id: str,
            id_fields: List[str],
            tiers_tab: str,
            tiers_field: str,
            sort_tab: str,
            rating_field: str,
            rank_field: str,
            on_update: Callable[[Sheet, int, List[str]], None]
    ):
        self.spreadsheet_id = spreadsheet_id
        self.id_fields = id_fields

        self.tiers_tab = tiers_tab
        self.tiers_field = tiers_field

        self.sort_tab = sort_tab
        self.rating_field = rating_field
        self.rank_field = rank_field

        self.on_update = on_update


RATING_FIELD = "Rating"
TITLE_FIELD = "Title"
ERA_FIELD = "Era"
RANK_FIELD = "Rank"
DIFF_FIELD = "Diff"
SHOW_DIFF_FIELD = "+/-"


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

    # =IF(C2="", 0, ROW(A2)-1 -C2)
    rank_row = f'{sheet.column(RANK_FIELD)}{index + 2}'
    diff_formula = f'=IF({rank_row}="", 0, ROW(A{index + 2})-1 -{rank_row})'
    sheet.update(row, DIFF_FIELD, diff_formula, print_diff=False)

    # =IF(B2>0, CONCAT("↓", B2), IF(B2<0, CONCAT("↑", -B2), ""))
    diff_row = f'{sheet.column(DIFF_FIELD)}{index + 2}'
    show_diff_formula = f'=IF({diff_row}>0, CONCAT("↓", {diff_row}), IF({diff_row}<0, CONCAT("↑", -{diff_row}), ""))'
    sheet.update(row, SHOW_DIFF_FIELD, show_diff_formula, print_diff=False)


SWIZZLES: TierSheet = TierSheet(
    spreadsheet_id=SWIZZLE_ID,
    id_fields=["Sort"],
    tiers_tab="Notes",
    tiers_field="Ratings",
    sort_tab="Discography",
    rating_field=RATING_FIELD,
    rank_field=RANK_FIELD,
    on_update=update_swizzle,
)
