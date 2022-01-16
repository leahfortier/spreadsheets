from typing import List, Dict

from main.util.constants import CHAPTER, MODE, RESERVED, SPREADSHEET_ID
from main.util.sheets import get_sheet_data


def is_empty(row: List[str]) -> bool:
    for val in row:
        if val != '':
            return False
    return True


class Data:
    def __init__(self, spreadsheet_id: str, range_name: str):
        values = get_sheet_data(spreadsheet_id, range_name)

        index = 0
        for index, row in enumerate(values):
            if not is_empty(values[index]):
                break

        full_schema = values[index]
        assert MODE in full_schema
        assert CHAPTER in full_schema

        self.player_names = [name for name in full_schema if name != '' and name not in RESERVED]

        self.schema: Dict[str, int] = {}
        for i, val in enumerate(full_schema):
            self.schema[val] = i

        self.rows: List[List[str]] = values[index + 1:]

    def has(self, key: str):
        return key in self.schema

    def get(self, key: str, row: List[str]) -> str:
        if not self.has(key):
            print("Key '" + key + "' not in schema.")
            return ""

        value: str = row[self.schema.get(key)]
        return value


def read_item_sheet(tab_name: str) -> Data:
    return Data(SPREADSHEET_ID, tab_name)
