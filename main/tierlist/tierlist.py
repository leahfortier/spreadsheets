from typing import List, Tuple, Any, Dict

from constants.io import SORTED_OUTFILE, EMPTY_CHAR
from data import RatingField, TierSheet
from util.data import Sheet
from util.file_io import to_tsv
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

    return tiers


class TierList:
    def __init__(self, config: TierSheet):
        self.config = config

        self.tiers = get_tiers(config.spreadsheet_id, config.tiers_tab, config.tiers_field, config.num_tier_categories)
        self.sheet = Sheet(get_sheet_data(config.spreadsheet_id, config.sort_tab), id_fields=config.id_fields)

        self._rating_field = self.config.rating_fields[0]

    def sort_by_id(self, key: Tuple[str, ...]) -> Any:
        return self.sheet.id_map[key]

    def sort_by_rank(self, key: Tuple[str, ...]) -> Tuple[int, int]:
        index = self.sheet.id_map[key]
        row = self.sheet.rows[index]
        rating = self.sheet.get(row, self._rating_field.rating)
        if rating == "":
            rating = EMPTY_CHAR

        # Sort first based on tier, and second based on current ordering
        tier_index = self.tiers[rating]
        rank = int(self.sheet.get(row, self._rating_field.rank))
        return tier_index, rank

    # Outputs a full sheet replacement in the new ordering
    def rank(self, rating_field: RatingField = None) -> List[List[str]]:
        rating_field = rating_field or self._rating_field
        self._rating_field = rating_field

        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())
        keys.sort(key=self.sort_by_rank)

        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            # Update sort index with current ordering -- +1 because zero-indexed
            self.sheet.update(row, rating_field.rating, str(i + 1), print_diff=False)

            if rating_field.show_diffs:
                # Update new sort index to dynamically get row order
                self.sheet.update(row, rating_field.rank, f'=ROW(A{i + 2}) - 1', print_diff=False)
                self.sheet.update(row, rating_field.show_diffs.old_rank_field, str(i + 1), print_diff=False)

                # =IF(C2-B2>0, CONCAT("↑", C2-B2), IF(C2-B2<0, CONCAT("↓", -(C2-B2)), ""))
                new_rank_row = f'{self.sheet.column(rating_field.rank)}{i + 2}'
                old_rank_row = f'{self.sheet.column(rating_field.show_diffs.old_rank_field)}{i + 2}'
                diff_row = f'{new_rank_row}-{old_rank_row}'
                diff_formula = (f'=IF({diff_row}>0, CONCAT("↓", {diff_row}), '
                                f'IF({diff_row}<0, CONCAT("↑", -({diff_row})), ""))')
                self.sheet.update(row, rating_field.show_diffs.diff_field, diff_formula, print_diff=False)

            self.config.on_update(self.sheet, i, row)
            rows.append(row)

        return rows

    # Outputs a subset of columns that maintains the current sheet ordering  instead of replacing the full sheet
    def get_rank_columns(self) -> List[List[str]]:
        for rating_field in self.config.rating_fields:
            self.rank(rating_field)

        # Get all output columns
        schema_fields = []
        for rating_field in self.config.rating_fields:
            schema_fields.append(rating_field.rank)
            if rating_field.show_diffs:
                schema_fields.append(rating_field.show_diffs.old_rank_field)
                schema_fields.append(rating_field.show_diffs.diff_field)
        schema_fields.sort(key=lambda field_name: self.sheet.schema[field_name])

        # Columns must be adjacent in the sheet or pasting is annoying
        for i in range(1, len(schema_fields)):
            assert self.sheet.schema[schema_fields[i]] == self.sheet.schema[schema_fields[i - 1]] + 1

        rows = []
        for row in self.sheet.rows:
            ranks = [self.sheet.get(row, field) for field in schema_fields]
            rows.append(ranks)
        return rows


def sort_tiers(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_sheet = tierlist.rank()
    to_tsv(SORTED_OUTFILE, sorted_sheet, show_diff=False)


def sort_columns(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_columns = tierlist.get_rank_columns()
    to_tsv(SORTED_OUTFILE, sorted_columns, show_diff=False)
