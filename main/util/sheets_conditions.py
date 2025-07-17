from typing import Self, Generic

from util.data import Sheet
from util.general import FieldsEnum, to_str
from util.sheets_formulas import column_range, Progress, index_value, get_progress, or_progress


# like from an organizational pov this would probably be in the sheet_formulas file,
# but it causes circular import so just separating out
class Column(Generic[FieldsEnum]):
    def __init__(self, sheet: Sheet, tab: str, field: FieldsEnum):
        self.start_index = 2
        self.col_range = column_range(sheet.column(field), self.start_index, tab=tab)
        self.address = index_value(self.col_range, self.start_index)

    def _with_value(self, value: str) -> Self:
        self.value = value
        self.condition = f"{self.col_range}, {self.value}"  # Used for ranges across the whole column
        self.row_condition = f"{self.address}={self.value}"  # Used for single row in the column
        return self

    def with_string(self, value: str) -> Self:
        value = to_str(value)
        return self._with_value(f'"{value}"')

    def with_checkbox(self) -> Self:
        return self._with_value("TRUE")

    def with_false_checkbox(self) -> Self:
        return self._with_value("FALSE")

    def count(self, *conditions: str) -> str:
        return self.progress(*conditions).count

    def progress(self, *conditions: str) -> Progress:
        return get_progress(self.condition, *conditions)

    def or_progress(self, first_condition: str, second_condition: str) -> Progress:
        return or_progress(self.condition, first_condition, second_condition)
