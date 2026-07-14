from typing import List, Dict

from main.util.data import Sheet
from pokopia.constants.pokes import NUM_FAVORITES
from pokopia.constants.sheets import get_ref_sheet, RefFields, get_db_sheet, DbFields


class PokeRow:
    def __init__(self, sheet: Sheet, row: List[str]):
        self.name = sheet.get(row, DbFields.NAME)
        self.faves = []
        for offset in range(0, NUM_FAVORITES):
            fave_index = sheet.schema[DbFields.FAVORITES] + offset

            self.faves.append(row[fave_index])


class Ref:
    def __init__(self):
        self.ref_sheet: Sheet = get_ref_sheet()
        self.db_sheet: Sheet = get_db_sheet()

        self.db: Dict[str, PokeRow] = {}
        self.favorites: List[str] = []

        for row in self.ref_sheet.rows:
            fave = self.ref_sheet.get(row, RefFields.FAVORITES)
            if fave:
                self.favorites.append(fave)

        for row in self.db_sheet.rows:
            poke = PokeRow(self.db_sheet, row)
            self.db[poke.name] = poke
