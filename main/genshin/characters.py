from typing import List

from genshin.constants.sheets import CharacterFields, Tab, get_sheet
from util.data import Sheet


class CharacterRow:
    def __init__(self, sheet: Sheet, row: List[str]):
        self.name = sheet.get(row, CharacterFields.NAME)
        self.boss_mat = sheet.get(row, CharacterFields.BOSS_MATERIAL)
        self.enemy_mat = sheet.get(row, CharacterFields.ENEMY_MATERIAL)
        self.local = sheet.get(row, CharacterFields.LOCAL_SPECIALTY)
        self.book = sheet.get(row, CharacterFields.TALENT_BOOK)
        self.trounce = sheet.get(row, CharacterFields.TROUNCE_TALENT)
        self.recipe = sheet.get(row, CharacterFields.RECIPE)


class CharacterSheet:
    def __init__(self):
        self.sheet: Sheet = get_sheet(Tab.CHARACTER_DATA)

        self.rows = []
        for row in self.sheet.rows:
            self.rows.append(CharacterRow(self.sheet, row))


