from typing import List, Tuple, Any

from constants.io import SORTED_OUTFILE
from constants.sheets import TierSheet
from util.data import Sheet
from util.file_io import to_tsv
from util.sheets_parse import get_sheet_data


def get_tiers(spreadsheet_id: str, tiers_tab: str, tiers_field: str) -> List[str]:
    tiers_tab = Sheet(get_sheet_data(spreadsheet_id, tiers_tab))
    tiers = []
    for row in tiers_tab.rows:
        tier = tiers_tab.get(row, tiers_field)
        if tier == "":
            break
        tiers.append(tier)
    return tiers


class TierList:
    def __init__(
            self,
            config: TierSheet,
    ):
        self.config = config

        tiers = get_tiers(config.spreadsheet_id, config.tiers_tab, config.tiers_field)
        self.tiers = {tier: index for index, tier in enumerate(tiers)}
        self.sheet = Sheet(get_sheet_data(config.spreadsheet_id, config.sort_tab), id_fields=config.id_fields)

    def sort_key(self, key: Tuple[str, ...]) -> Any:
        index = self.sheet.id_map[key]
        row = self.sheet.rows[index]
        rating = self.sheet.get(row, self.config.rating_field)

        # Sort first based on tier, and second based on current ordering
        tier_index = self.tiers[rating]
        rank = int(self.sheet.get(row, self.config.new_rank_field))
        return tier_index, rank

    def sort_tiers(self) -> List[List[str]]:
        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())
        keys.sort(key=self.sort_key)

        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            # Update new sort index to dynamically get row order
            self.sheet.update(row, self.config.new_rank_field, f'=ROW(A{i + 2}) - 1', print_diff=False)

            # Update old sort index with current ordering -- +1 because zero-indexed
            if self.config.old_rank_field:
                self.sheet.update(row, self.config.old_rank_field, str(i + 1), print_diff=False)

            # =IF(C2-B2>0, CONCAT("↑", C2-B2), IF(C2-B2<0, CONCAT("↓", -(C2-B2)), ""))
            new_rank_row = f'{self.sheet.column(self.config.new_rank_field)}{i + 2}'
            old_rank_row = f'{self.sheet.column(self.config.old_rank_field)}{i + 2}'
            diff_row = f'{new_rank_row}-{old_rank_row}'
            diff_formula = (f'=IF({diff_row}>0, CONCAT("↓", {diff_row}), '
                            f'IF({diff_row}<0, CONCAT("↑", -({diff_row})), ""))')
            self.sheet.update(row, self.config.diff_field, diff_formula, print_diff=False)

            self.config.on_update(self.sheet, i, row)
            rows.append(row)

        return rows


def sort_tiers(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_list = tierlist.sort_tiers()
    to_tsv(SORTED_OUTFILE, sorted_list, show_diff=False)
