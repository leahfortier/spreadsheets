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

    def sort_by_id(self, key: Tuple[str, ...]) -> Any:
        return self.sheet.id_map[key]

    def sorted_keys(self, rating_field: RatingField) -> List[Tuple[str, ...]]:
        def sort_by_rank(key: Tuple[str, ...]) -> Tuple[int, int]:
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]
            rating = self.sheet.get(row, rating_field.rating)
            if rating == "":
                rating = EMPTY_CHAR

            # Sort first based on tier, and second based on current ordering
            tier_index = self.tiers[rating]
            rank = int(self.sheet.get(row, rating_field.rank))
            return tier_index, rank

        keys: List[Tuple[str, ...]] = list(self.sheet.id_map.keys())
        keys.sort(key=sort_by_rank)

        return keys

    # Handles manual functions that are dependent on the output order
    def handle_dynamic(self, rating_field: RatingField, output_index: int, row: List[str]) -> None:
        # Update new sort index to dynamically get row order
        if self.config.dynamic_rank_field:
            self.sheet.update(row, self.config.dynamic_rank_field, f'=ROW(A{output_index + 2}) - 1', print_diff=False)

        # =IF(C2-B2>0, CONCAT("↑", C2-B2), IF(C2-B2<0, CONCAT("↓", -(C2-B2)), ""))
        if rating_field.diff:
            assert self.config.dynamic_rank_field

            current_rank_row = f'{self.sheet.column(self.config.dynamic_rank_field)}{output_index + 2}'
            previous_rank_row = f'{self.sheet.column(rating_field.rank)}{output_index + 2}'
            diff_row = f'{current_rank_row}-{previous_rank_row}'
            diff_formula = (f'=IF({diff_row}>0, CONCAT("↓", {diff_row}), '
                            f'IF({diff_row}<0, CONCAT("↑", -({diff_row})), ""))')
            self.sheet.update(row, rating_field.diff, diff_formula, print_diff=False)

        self.config.manual_update(self.sheet, output_index, row)

    def rank(self, rating_field: RatingField = None) -> None:
        keys = self.sorted_keys(rating_field)
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            # Update sort index with current ordering -- +1 because zero-indexed
            self.sheet.update(row, rating_field.rank, str(i + 1), print_diff=False)

    # Outputs a full sheet replacement in the new ordering
    def get_rank_sheet(self) -> List[List[str]]:
        assert len(self.config.rating_fields) == 1

        rating_field = self.config.rating_fields[0]
        self.rank(rating_field)

        # Output order changes to updated rank order
        keys = self.sorted_keys(rating_field)
        rows = []
        for i, key in enumerate(keys):
            index = self.sheet.id_map[key]
            row = self.sheet.rows[index]

            self.handle_dynamic(rating_field, i, row)
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
            if rating_field.diff:
                schema_fields.append(rating_field.diff)
        if self.config.dynamic_rank_field:
            schema_fields.append(self.config.dynamic_rank_field)
        schema_fields.sort(key=lambda field_name: self.sheet.schema[field_name])

        # Columns must be adjacent in the sheet or pasting is annoying
        for i in range(1, len(schema_fields)):
            assert self.sheet.schema[schema_fields[i]] == self.sheet.schema[schema_fields[i - 1]] + 1

        # Output stays in the same exact order as the input
        rows = []
        for i, row in enumerate(self.sheet.rows):
            for rating_field in self.config.rating_fields:
                self.handle_dynamic(rating_field, i, row)
            ranks = [self.sheet.get(row, field) for field in schema_fields]
            rows.append(ranks)
        return rows


def sort_tiers(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_sheet = tierlist.get_rank_sheet()
    to_tsv(SORTED_OUTFILE, sorted_sheet, show_diff=False)


def sort_columns(sheet: TierSheet):
    tierlist = TierList(sheet)

    sorted_columns = tierlist.get_rank_columns()
    to_tsv(SORTED_OUTFILE, sorted_columns, show_diff=False)
