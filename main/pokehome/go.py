from typing import List, Tuple

from main.pokehome.constants.io import GO_SHADOW_INFILE, GO_OUTFILE
from main.pokehome.constants.sheets import DokuFields, get_go_sheet, GoFields
from main.pokehome.db import DbRow, Database
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv


def to_go_row(db_row: DbRow, sheet: Sheet) -> List[str]:
    print_diff = True

    def update(field: GoFields, value: str):
        sheet.update(sheet_row, field.value, value, print_diff)

    key: Tuple[str] = (db_row.id,)
    index = sheet.id_map.get(key, None)
    if index is None:
        print(f"Adding go row for {db_row.id} {db_row.name}")
        sheet_row = ["FALSE"] * len(sheet.schema_row)
        print_diff = False
        update(GoFields.ID, db_row.id)
    else:
        sheet_row = sheet.rows[index]

    update(GoFields.NAME, db_row.name)
    update(GoFields.REGION, db_row.region)

    sheet.set(sheet_row, DokuFields.IMAGE, db_row.image)

    return sheet_row


def get_go_ids(db: Database) -> List[str]:
    # https://bulbapedia.bulbagarden.net/wiki/List_of_Shadow_Pok%C3%A9mon_in_Pok%C3%A9mon_GO
    in_rows: List[List[str]] = from_tsv(GO_SHADOW_INFILE)
    out_rows: List[str] = []

    for index, row in enumerate(in_rows):
        if index % 2 == 1:
            continue

        assert len(row) == 4
        num = row[0]
        species = row[2]

        db_row = db.get(num)
        assert db_row.species == species

        if db_row.id in out_rows:
            continue

        out_rows.append(db_row.id)

    return out_rows


class GoDex:
    def __init__(self, db: Database):
        self.sheet: Sheet = get_go_sheet()
        self.rows: List[DbRow] = []

        ids = get_go_ids(db)

        for poke_id in ids:
            db_row = db.get(poke_id)
            self.rows.append(db_row)

    def write(self):
        out_rows: List[List[str]] = [to_go_row(db_row, self.sheet) for db_row in self.rows]
        to_tsv(GO_OUTFILE, out_rows, show_diff=False)
