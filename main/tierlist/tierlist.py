from typing import List, Tuple, Any, Dict

from constants.io import SORTED_OUTFILE, EMPTY_CHAR
from constants.sheets import TierSheet
from util.data import Sheet
from util.file_io import to_tsv, to_file
from util.sheets_parse import get_sheet_data


def get_tiers(spreadsheet_id: str, tiers_tab: str, tiers_field: str, num_tier_categories: int = 1) -> Dict[str, int]:
    if num_tier_categories < 1:
        print("Invalid number of tiers:", num_tier_categories)
        return {}

    tiers_tab = Sheet(get_sheet_data(spreadsheet_id, tiers_tab))
    tiers = {}
    for row_index, row in enumerate(tiers_tab.rows):
        tiers_index = tiers_tab.schema.get(tiers_field)
        if row[tiers_index] == "":
            break

        for tier_col_index in range(num_tier_categories):
            col_index = tiers_index + tier_col_index
            if col_index < len(row):
                tier = row[tiers_index + tier_col_index]
                if tier:
                    tiers[tier] = row_index

    tiers[EMPTY_CHAR] = len(tiers_tab.rows)

    print("Tiers:", tiers)
    return tiers


class TierList:
    def __init__(
            self,
            config: TierSheet,
    ):
        self.config = config

        self.tiers = get_tiers(config.spreadsheet_id, config.tiers_tab, config.tiers_field, config.num_tier_categories)
        self.sheet = Sheet(get_sheet_data(config.spreadsheet_id, config.sort_tab), id_fields=config.id_fields)

    def sort_by_id(self, key: Tuple[str, ...]) -> Any:
        return self.sheet.id_map[key]

    def sort_by_rank(self, key: Tuple[str, ...]) -> Any:
        index = self.sheet.id_map[key]
        row = self.sheet.rows[index]
        rating = self.sheet.get(row, self.config.rating_field)
        if rating == "":
            rating = EMPTY_CHAR

        # Sort first based on tier, and second based on current ordering
        tier_index = self.tiers[rating]
        rank = int(self.sheet.get(row, self.config.new_rank_field))
        return tier_index, rank

    def rank(self) -> List[List[str]]:
        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())
        keys.sort(key=self.sort_by_rank)

        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            # Update sort index with current ordering -- +1 because zero-indexed
            if self.config.old_rank_field:
                # Update new sort index to dynamically get row order
                self.sheet.update(row, self.config.new_rank_field, f'=ROW(A{i + 2}) - 1', print_diff=False)
                self.sheet.update(row, self.config.old_rank_field, str(i + 1), print_diff=False)
            else:
                self.sheet.update(row, self.config.new_rank_field, str(i + 1), print_diff=False)

            if self.config.diff_field:
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

    def get_rank_column(self) -> List[str]:
        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())

        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            rank = self.sheet.get(row, self.config.new_rank_field)
            rows.append(rank)

        return rows




def sort_tiers(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_list = tierlist.rank()
    to_tsv(SORTED_OUTFILE, sorted_list, show_diff=False)


def sort_column(sheet: TierSheet):
    tierlist = TierList(sheet)

    tierlist.rank()
    sorted_column = tierlist.get_rank_column()

    to_file(SORTED_OUTFILE, sorted_column, show_diff=False)