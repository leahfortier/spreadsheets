from typing import List, Dict

from main.celeste.constants import CHAPTER, MODE, RESERVED
from main.celeste.data.scoreboard import Scoreboard


def is_empty(row: List[str]) -> bool:
    for val in row:
        if val != '':
            return False
    return True


class Data:
    def __init__(self, values: List[List[str]]):
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
            print(f'Key {key} not in schema.')
            return ''

        return row[self.schema.get(key)]

    def to_board(self) -> Scoreboard:
        return Scoreboard(self.player_names, self.rows)
