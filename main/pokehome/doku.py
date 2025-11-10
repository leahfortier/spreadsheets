from typing import List, Tuple, Set, Self, Optional

from main.pokehome.constants.io import DOKU_OUTFILE, DOKU_DIFFS_OUTFILE
from main.pokehome.constants.sheets import DokuFields, get_doku_sheet, DexFields, SpriteType, \
    DOKU_TAB, get_doku_stats_sheet
from main.pokehome.db import DbRow, Database
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv
from pokehome.constants.pokes import DOKU_INCLUDE_GENDER_FORM, NON_DOKU_FORMS
from util.sheets_conditions import ColumnBuilder
from util.sheets_formulas import if_image
from util.time import today_str


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
    update(DokuFields.EVO_TYPE, db_row.evolution_type)
    update(DokuFields.HAS_BRANCH, db_row.has_branch_evo)
    update(DokuFields.IS_BABY, db_row.baby)
    update(DokuFields.IS_FOSSIL, db_row.fossil)
    update(DokuFields.IS_PARTNER, db_row.partner)
    update(DokuFields.IS_LEGENDARY, db_row.legendary)
    update(DokuFields.IS_MYTHICAL, db_row.mythical)
    update(DokuFields.IS_PARADOX, db_row.paradox)
    update(DokuFields.IS_ULTRA_BEAST, db_row.ultra)

    shiny_col = ColumnBuilder(sheet, DOKU_TAB, DexFields.SHINY).with_checkbox().build()
    image_url = db_row.get_image_url(SpriteType.NORMAL)
    shiny_url = db_row.get_image_url(SpriteType.SHINY)
    image = if_image(shiny_col.row_condition, shiny_url, image_url)
    sheet.set(sheet_row, DokuFields.IMAGE, image)

    return sheet_row


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

        self.diffs: DokuDiffs = DokuDiffs()

    def write(self):
        out_rows: List[List[str]] = [to_doku_row(db_row, self.sheet) for db_row in self.rows]
        to_tsv(DOKU_OUTFILE, out_rows, show_diff=False)

        self.diffs.write()


class DokuDiff:
    def __init__(self, remaining: int, total: int, row_name: str, col_name: str, date: str = None):
        self.remaining = remaining
        self.total = total
        self.row_name = row_name.strip()
        self.col_name = col_name.strip()
        self.category = f'{self.row_name} / {self.col_name}'
        self.reverse = f'{self.col_name} / {self.row_name}'
        self.date = date or today_str()

        self.message = f'{self.remaining} / {self.total} {self.category}'

    def finished(self) -> bool:
        return self.remaining == 0 and self.total > 0

    def to_out_row(self) -> List[str]:
        return [self.date, str(self.total), self.category]

    @staticmethod
    def from_out_row(row: List[str]) -> "DokuDiff":
        date, total, category = row

        index = category.index("/")
        row_name = category[:index]
        col_name = category[index + 1:]

        return DokuDiff(0, int(total), row_name, col_name, date)


class DokuDiffs:
    def __init__(self):
        self.stats_sheet: Sheet = get_doku_stats_sheet()

        out_rows: List[List[str]] = from_tsv(DOKU_DIFFS_OUTFILE)
        self.out_diffs: List[DokuDiff] = [DokuDiff.from_out_row(row) for row in out_rows]
        self.seen_categories: Set[str] = {diff.category for diff in self.out_diffs}

        self.stats_diffs: List[DokuDiff] = []
        for row in self.stats_sheet.rows:
            for schema_index, value in enumerate(row):
                diff = self.create_diff(schema_index, value, row)
                if diff:
                    self.stats_diffs.append(diff)
                    if diff.finished() and not self.seen(diff):
                        print(f"Finished {diff.category}!! ({diff.total})")
                        self.out_diffs.append(diff)
                        self.seen_categories.add(diff.category)

    def seen(self, diff: DokuDiff) -> bool:
        return diff.category in self.seen_categories or diff.reverse in self.seen_categories

    def create_diff(self, schema_index: int, value: str, row: List[str]) -> Optional[DokuDiff]:
        if "/" not in value:
            return None

        index = value.index("/")
        remaining = int(value[:index])
        total = int(value[index + 1:])

        row_name = self.stats_sheet.get(row, "Category").removesuffix("-Type")
        col_name = self.stats_sheet.rows[0][schema_index]

        if row_name == col_name and total > 0:
            row_name = "All"
        if col_name == "Total":
            remaining = total - remaining
            col_name = row_name
            row_name = "All"

        return DokuDiff(remaining, total, row_name, col_name)

    def write(self):
        to_tsv(DOKU_DIFFS_OUTFILE, [diff.to_out_row() for diff in self.out_diffs])
