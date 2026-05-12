from typing import List, Dict, Optional, Tuple

from main.util.general import is_empty, FieldsEnum, to_str
from util.sheets_formulas import column_name

CHECKBOX_TRUE = "TRUE"
CHECKBOX_FALSE = "FALSE"


class Sheet:
    def __init__(
            self,
            rows: List[List[str]],
            auto_fields: List[FieldsEnum] = None,
            escape_fields: List[FieldsEnum] = None,
            id_fields: List[FieldsEnum] = None,
            break_schema_field: str = None,
            schema_size=1,
            allow_duplicate_keys=False,
    ):
        index = 0
        for index, row in enumerate(rows):
            if not is_empty(rows[index]):
                break

        self.schema_row: List[str] = rows[index]
        self.schema: Dict[str, int] = {}

        self.auto_fields: List[str] = auto_fields or []
        self.escape_fields: List[str] = escape_fields or []
        self.id_fields: List[str] = id_fields or []
        self.id_map: Dict[Tuple[str, ...], int] = {}
        self.allow_duplicate_keys = allow_duplicate_keys

        if break_schema_field:
            self.break_index = self.schema_row.index(break_schema_field)
        else:
            self.break_index = len(self.schema_row)
        self.schema_row = self.schema_row[:self.break_index]

        for i, val in enumerate(self.schema_row):
            self.schema[val] = i

        self.rows_start_index = index + schema_size
        self.rows: List[List[str]] = [row[:self.break_index] for row in rows[self.rows_start_index:]]
        for row_index, row in enumerate(self.rows):
            if len(row) < len(self.schema_row):
                row += [""] * (len(self.schema_row) - len(row))
                self.rows[row_index] = row

            row_id = self._create_id(row)
            if row_id:
                self.id_map[row_id] = row_index
            # Auto fields should be set to empty since they will automatically repopulate
            for field in self.auto_fields:
                self.set(row, field, '')
            for field in self.escape_fields:
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

    # Identical to set except will print if different
    def update(self, row: List[str], field: str, new_value: str):
        field = to_str(field)
        existing_value = self.get(row, field)
        if existing_value != new_value:
            self.set(row, field, new_value)
            print(f"{self.get_id(row)}: {field} updated from {existing_value} -> {to_str(new_value)}: {row}")

    def get_id(self, row: List[str], id_index: int = None) -> Optional[Tuple[str, ...]]:
        if self.id_fields:
            id_values = [self.get(row, field) for field in self.id_fields]
            if id_index:
                id_values += [id_index]
            elif self.allow_duplicate_keys:
                id_values += ["<index>"]
            return tuple(id_values)
        return id_index

    def _create_id(self, row: List[str]) -> Optional[Tuple[str, ...]]:
        # Add a count index if sheet allows duplicate keys
        if self.allow_duplicate_keys:
            id_index = 0
            while True:
                new_id = self.get_id(row, id_index)
                if new_id not in self.id_map:
                    return new_id
                id_index += 1

        new_id = self.get_id(row)
        assert new_id not in self.id_map, new_id
        return new_id

    # Ex: "A", "B"
    def column(self, field: str) -> str:
        index = self.schema[field]
        return column_name(index)

    # Ex: "A2", "B3"
    def column_field(self, field: str, row_index: int) -> str:
        return f'{self.column(field)}{self.rows_start_index + row_index}'

    def has_field(self, field: str) -> bool:
        return to_str(field) in self.schema
