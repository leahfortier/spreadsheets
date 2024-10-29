from typing import List, Tuple

from main.pokehome.constants.io import DOKU_OUTFILE
from main.pokehome.constants.sheets import DokuFields, get_doku_sheet, DokuFormType
from main.pokehome.db import DbRow, Database
from main.util.data import Sheet
from main.util.file_io import to_tsv
from pokehome.constants.pokes import REGIONALS, DOKU_INCLUDE_GENDER_FORM, NON_DOKU_FORMS


def to_doku_row(db_row: DbRow, sheet: Sheet) -> List[str]:
    print_diff = True

    def update(field: DokuFields, value: str):
        sheet.update(sheet_row, field.value, value, print_diff)

    key: Tuple[str] = (db_row.id,)
    index = sheet.id_map.get(key, None)
    if index is None:
        print(f"Adding doku row for {db_row.id} {db_row.name}")
        sheet_row = [""] * len(sheet.schema_row)
        print_diff = False
        update(DokuFields.ID, db_row.id)
        update(DokuFields.DEX, "FALSE")
    else:
        sheet_row = sheet.rows[index]

    update(DokuFields.NAME, db_row.name)
    update(DokuFields.GENERATION, db_row.generation)
    update(DokuFields.REGION, db_row.region)
    update(DokuFields.TYPE1, db_row.type1)
    update(DokuFields.TYPE2, db_row.type2)
    update(DokuFields.BRANCH_EVO, db_row.has_branch_evo)
    update(DokuFields.FORM, get_doku_form(db_row).value)
    update(DokuFields.EVO_TYPE, db_row.evolution_type)

    sheet.set(sheet_row, DokuFields.IMAGE, db_row.image)

    return sheet_row


def get_doku_form(db_row: DbRow) -> DokuFormType:
    if db_row.is_base_form(regional_is_base=True):
        return DokuFormType.BASE
    elif db_row.digimon_form.startswith("Mega"):
        return DokuFormType.MEGA
    elif db_row.digimon_form == "Gigantamax":
        return DokuFormType.GMAX
    elif db_row.digimon_form in REGIONALS:
        return DokuFormType.REGIONAL
    elif db_row.gender_id and db_row.species in DOKU_INCLUDE_GENDER_FORM:
        return DokuFormType.GENDER
    return DokuFormType.ALT


def is_doku_form(db_row: DbRow) -> bool:
    if db_row.is_base_form(regional_is_base=True):
        return True
    if db_row.digimon_form:
        return True
    if db_row.name == "Floette (Eternal Flower)":
        return True
    if db_row.species in NON_DOKU_FORMS:
        return False
    if db_row.gender_id:
        return db_row.species in DOKU_INCLUDE_GENDER_FORM
    if db_row.form:
        return True
    if db_row.regional_form:
        return True
    return False


class Doku:
    def __init__(self, db: Database):
        self.sheet: Sheet = get_doku_sheet()
        self.rows: List[DbRow] = []

        for db_row in db.rows:
            if is_doku_form(db_row):
                self.rows.append(db_row)

    def write(self):
        out_rows: List[List[str]] = [to_doku_row(db_row, self.sheet) for db_row in self.rows]
        to_tsv(DOKU_OUTFILE, out_rows)
