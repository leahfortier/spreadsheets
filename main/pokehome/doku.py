from typing import Dict, List, Tuple

from main.pokehome.boxes import Boxes, Box
from main.pokehome.constants.io import DEX_OUTFILE, DOKU_OUTFILE
from main.pokehome.constants.pokes import REGIONALS, BOX_COLS, FORM_BOXES, NON_DOKU_FORMS
from main.pokehome.constants.sheets import DexFields, get_dex_sheet, HiddenAbilityProgress, EMPTY_ABILITY, \
    DexClassification, DokuFields, get_doku_sheet
from main.pokehome.db import DbRow, Database
from main.util.data import Sheet
from main.util.file_io import to_tsv


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
    update(DokuFields.REGION, db_row.region)
    update(DokuFields.TYPE1, db_row.type1)
    update(DokuFields.TYPE2, db_row.type2)

    sheet.set(sheet_row, DokuFields.IMAGE, db_row.image)

    return sheet_row


class Doku:
    def __init__(self, db: Database):
        self.sheet: Sheet = get_doku_sheet()
        self.rows: List[DbRow] = []

        for db_row in db.rows:
            if db_row.is_doku_form():
                self.rows.append(db_row)

    def write(self):
        out_rows: List[List[str]] = [to_doku_row(db_row, self.sheet) for db_row in self.rows]
        to_tsv(DOKU_OUTFILE, out_rows)
