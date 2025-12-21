from typing import Self, Generic

from util.data import Sheet, CHECKBOX_FALSE, CHECKBOX_TRUE
from util.general import FieldsEnum, to_str
from util.sheets_formulas import column_range, Progress, index_value, get_progress, or_progress


# like from an organizational pov this would probably be in the sheet_formulas file,
# but it causes circular import so just separating out
class Column:
    def __init__(self, col_range: str, address: str, condition_value: str):
        self.col_range = col_range
        self.address = address
        self.condition = f"{self.col_range}, {condition_value}"   # Used for ranges across the whole column
        self.row_condition = f"{self.address}={condition_value}"  # Used for single row in the column

    def count(self, *conditions: str) -> str:
        return self.progress(*conditions).count

    def progress(self, *conditions: str) -> Progress:
        return get_progress(self.condition, *conditions)

    def or_progress(self, first_condition: str, second_condition: str) -> Progress:
        return or_progress(self.condition, first_condition, second_condition)


class ColumnBuilder(Generic[FieldsEnum]):
    def __init__(self, sheet: Sheet, tab: str, field: FieldsEnum):
        start_index = sheet.rows_start_index + 1
        self.col_range = column_range(sheet.column(field), start_index, tab=tab)
        self.address = index_value(self.col_range, start_index)

    def _with_value(self, value: str) -> Self:
        self.value = value
        return self

    def with_string(self, value: str) -> Self:
        value = to_str(value)
        return self._with_value(f'"{value}"')

    def with_checkbox(self) -> Self:
        return self._with_value(CHECKBOX_TRUE)

    def with_false_checkbox(self) -> Self:
        return self._with_value(CHECKBOX_FALSE)

    def build(self) -> Column:
        return Column(self.col_range, self.address, self.value)
