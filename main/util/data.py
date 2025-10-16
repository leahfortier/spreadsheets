from typing import List, Dict, Optional, Tuple

from main.util.general import is_empty, FieldsEnum, to_str
from util.sheets_formulas import column_name


class Sheet:
    def __init__(
            self,
            rows: List[List[str]],
            escape_fields: List[FieldsEnum] = None,
            id_fields: List[FieldsEnum] = None,
            break_schema_field: str = None
    ):
        index = 0
        for index, row in enumerate(rows):
            if not is_empty(rows[index]):
                break

        self.schema_row: List[str] = rows[index]
        self.schema: Dict[str, int] = {}

        self.escape_fields: List[str] = escape_fields or []
        self.id_fields: List[str] = id_fields or []
        self.id_map: Dict[Tuple[str, ...], int] = {}

        if break_schema_field:
            self.break_index = self.schema_row.index(break_schema_field)
        else:
            self.break_index = len(self.schema_row)
        self.schema_row = self.schema_row[:self.break_index]

        for i, val in enumerate(self.schema_row):
            self.schema[val] = i

        self.rows: List[List[str]] = [row[:self.break_index] for row in rows[(index + 1):]]
        for row_index, row in enumerate(self.rows):
            if len(row) < len(self.schema_row):
                row += [""] * (len(self.schema_row) - len(row))
                self.rows[row_index] = row

            row_id = self.get_id(row)
            if row_id:
                self.id_map[row_id] = row_index
            for field in escape_fields or []:
                value = self.get(row, field)
                self.set(row, field, value)

    def get(self, row: List[str], field: str) -> str:
        field = to_str(field)
        value = row[self.schema[field]]
        if field in self.escape_fields:
            return value.lstrip("'")
        return value

    def set(self, row: List[str], field: str, value: str):
        field = to_str(field)
        value = to_str(value)
        if field in self.escape_fields:
            value = value.lstrip("'")
            value = f"'{value}"
        row[self.schema[field]] = value

    def get_id(self, row: List[str]) -> Optional[Tuple[str, ...]]:
        if self.id_fields:
            return tuple([self.get(row, field) for field in self.id_fields])
        return None

    def update(self, row: List[str], field: str, new_value: str, print_diff=True):
        field = to_str(field)
        existing_value = self.get(row, field)
        if existing_value != new_value:
            self.set(row, field, new_value)
            if print_diff:
                print(f"{self.get_id(row)}: {field} updated from {existing_value} -> {to_str(new_value)}: {row}")

    def column(self, field: str) -> str:
        index = self.schema[field]
        return column_name(index)

    def has_field(self, field: str) -> bool:
        return to_str(field) in self.schema
