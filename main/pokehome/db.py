from typing import List, Dict

from main.pokehome.constants.io import DB_OUTFILE, EVOLUTIONS_INFILE
from main.pokehome.constants.pokes import INCLUDE_GENDER_FORM, EXCLUDE_BASE_FORM
from main.pokehome.constants.sheets import DbFields, get_db_sheet
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv


class DBRow:
    def __init__(self, sheet: Sheet, row: List[str]):
        self.dex = sheet.get(row, DbFields.DEX)
        self.form_id = sheet.get(row, DbFields.FORM_ID)
        self.gender_id = sheet.get(row, DbFields.GENDER_ID)

        self.species = sheet.get(row, DbFields.SPECIES)
        self.regional_form = sheet.get(row, DbFields.REGIONAL_FORM)
        self.form = sheet.get(row, DbFields.FORM)
        self.gender_form = sheet.get(row, DbFields.GENDER_FORM)

        self.ability1 = sheet.get(row, DbFields.ABILITY1)
        self.ability2 = sheet.get(row, DbFields.ABILITY2)
        self.hidden = sheet.get(row, DbFields.HIDDEN_ABILITY)

        self.family = sheet.get(row, DbFields.FAMILY_EVOS)
        self.region = sheet.get(row, DbFields.OG_REGION)

        self.id = self.dex + self.form_id + self.gender_id
        sheet.update(row, DbFields.ID, self.id)

        name_form = self.form
        if self.species == "Alcremie":
            name_form += " - " + self.gender_form
        if name_form:
            name_form = f"({name_form})"

        self.name = " ".join(filter(None, [self.regional_form, self.species, name_form]))
        sheet.update(row, DbFields.NAME, self.name)

        self.image = f'=image("https://pokejungle.net/sprites/normal/{self.id}.png")'
        self.shiny_image = f'=image("https://pokejungle.net/sprites/shiny/{self.id}.png")'
        sheet.set(row, DbFields.IMAGE, self.image)
        sheet.set(row, DbFields.SHINY_IMAGE, self.shiny_image)

    def is_base_form(self, regional_is_base=False) -> bool:
        if self.id == self.dex:
            return True
        if self.gender_id:
            return False
        if self.form:
            return False
        if regional_is_base and self.regional_form:
            return True
        print(self.name, "end of base form")
        return False

    def is_alt_form(self, regional_is_alt=False) -> bool:
        if self.is_base_form(not regional_is_alt) and self.species in EXCLUDE_BASE_FORM:
            return False
        if self.gender_id:
            return self.species in INCLUDE_GENDER_FORM
        if self.form:
            return True
        if regional_is_alt and self.regional_form:
            return True
        return False


class Database:
    def __init__(self):
        self.sheet: Sheet = get_db_sheet()
        self.rows: List[DBRow] = [DBRow(self.sheet, row) for row in self.sheet.rows]

        self.id_map: Dict[str, int] = {}
        self.species_map: Dict[str, List[str]] = {}
        self.regionals: Dict[str, List[str]] = {}

        for index, row in enumerate(self.rows):
            assert row.id not in self.id_map
            self.id_map[row.id] = index

            self.species_map.setdefault(row.species, []).append(row.id)
            if row.regional_form and row.is_base_form(regional_is_base=True):
                self.regionals.setdefault(row.regional_form, []).append(row.id)

    def get(self, poke_id: str) -> DBRow:
        return self.rows[self.id_map[poke_id]]

    def get_forms(self, names: List[str]) -> List[str]:
        forms: List[str] = []
        for name in names:
            for poke_id in self.species_map.get(name):
                row: DBRow = self.get(poke_id)
                if row.is_alt_form(regional_is_alt=False):
                    forms.append(poke_id)
        return forms

    def write(self):
        to_tsv(DB_OUTFILE, [row for row in self.sheet.rows])

