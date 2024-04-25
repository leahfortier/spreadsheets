from typing import List, Tuple, Any

from constants.io import SORTED_OUTFILE
from constants.sheets import TIERS_TAB, SORT_TAB, TIERS_FIELD, RATING_FIELD, SORT_FIELD, \
    RANK_FIELD, RANK_TAB_FIELD
from util.data import Sheet
from util.file_io import to_tsv
from util.sheets import get_sheet_data


class TierList:
    def __init__(
            self,
            tiers: List[str],
            sorted_sheet: Sheet,
    ):
        self.tiers = {tier: index for index, tier in enumerate(tiers)}
        self.sheet = sorted_sheet

    def sort_key(self, key: Tuple[str, ...]) -> Any:
        index = self.sheet.id_map[key]
        row = self.sheet.rows[index]
        rating = self.sheet.get(row, RATING_FIELD)

        # Sort first based on tier, and second based on current ordering
        tier_index = self.tiers[rating]
        old_value = int(self.sheet.get(row, RANK_FIELD))
        return tier_index, old_value

    def sort_tiers(self) -> List[List[str]]:
        # Update old sort value with current ordering
        for i, row in enumerate(self.sheet.rows):
            self.sheet.update(row, RANK_FIELD, str(i + 1))

        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())
        keys.sort(key=self.sort_key)

        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            # Update new sort index
            self.sheet.update(row, RANK_FIELD, str(i + 1), print_diff=False)

            # Manual ratings
            rating_formula = f'=FILTER(INDIRECT(F{i+2}&"!C$2:C"), B{i+2}=INDIRECT(F{i+2}&"!A$2:A"))'
            self.sheet.update(row, RATING_FIELD, rating_formula, print_diff=False)

            rows.append(row)

        return rows


def sort_tiers(spreadsheet_id: str):
    tiers_tab = Sheet(get_sheet_data(spreadsheet_id, TIERS_TAB))
    tiers = []
    for row in tiers_tab.rows:
        tier = tiers_tab.get(row, TIERS_FIELD)
        if tier == "":
            break
        tiers.append(tier)

    sorted_sheet = Sheet(get_sheet_data(spreadsheet_id, SORT_TAB), id_fields=[SORT_FIELD])
    tierlist = TierList(tiers, sorted_sheet)

    sorted_list = tierlist.sort_tiers()
    to_tsv(SORTED_OUTFILE, sorted_list, show_diff=False)
