from typing import Dict, List, Tuple

from main.pokehome.boxes import Boxes, Box
from main.pokehome.constants.io import DEX_OUTFILE
from main.pokehome.constants.pokes import REGIONALS, BOX_COLS, FORM_BOXES
from main.pokehome.constants.sheets import DexFields, get_dex_sheet, HiddenAbilityProgress, EMPTY_ABILITY, \
    DexClassification
from main.pokehome.db import DBRow, Database
from main.util.data import Sheet
from main.util.file_io import to_tsv


class DexRow:
    def __init__(self, index: int, box_name: str, dex_class: DexClassification, db_row: DBRow):
        self.box = box_name
        self.row_index = str(index // BOX_COLS + 1)
        self.col_index = str(index % BOX_COLS + 1)
        self.classification = dex_class

        self.row = db_row
        self.is_form = self.classification == DexClassification.FORMS

    def to_dex_row(self, sheet: Sheet) -> List[str]:
        print_diff = True

        def update(field: DexFields, value: str):
            sheet.update(sheet_row, field.value, value, print_diff)

        key: Tuple[str, ...] = (self.row.id, self.box)
        index = sheet.id_map.get(key, None)
        if index is None:
            print(f"Adding {'form' if self.is_form else 'base'} row for {self.row.id} {self.row.name} in dex")
            sheet_row = ["FALSE"] * len(sheet.schema_row)
            print_diff = False
            update(DexFields.ID, self.row.id)
            update(DexFields.NOTES, "")
            update(DexFields.TRAINER, "")
            update(DexFields.NICKNAME, "")
            update(DexFields.HIDDEN_PROGRESS, HiddenAbilityProgress.UNOBTAINED.value)
            if self.is_form:
                update(DexFields.ROW, "TODO")
                update(DexFields.COL, "TODO")
        else:
            sheet_row = sheet.rows[index]

        update(DexFields.NAME, self.row.name)
        update(DexFields.CLASS, self.classification)
        update(DexFields.REGION, self.row.region)

        update(DexFields.BOX, self.box)
        if not self.is_form:
            update(DexFields.ROW, self.row_index)
            update(DexFields.COL, self.col_index)

        update(DexFields.HIDDEN_ABILITY, self.row.hidden)
        if self.row.hidden == EMPTY_ABILITY:
            update(DexFields.HIDDEN_PROGRESS, HiddenAbilityProgress.NO_HIDDEN_ABILITY.value)

        sheet.set(sheet_row, DexFields.IMAGE, self.row.image)
        sheet.set(sheet_row, DexFields.SHINY_IMAGE, self.row.shiny_image)

        return sheet_row


class Dex:
    def __init__(self, db: Database):
        self.sheet: Sheet = get_dex_sheet()

        self.boxes = Boxes()
        self.base_rows: List[DexRow] = []
        self.form_rows: List[DexRow] = []
        form_to_box: Dict[str, str] = {}

        def add_base_box(box: Box, dex_class: DexClassification):
            for i, poke_id in enumerate(box.ids):
                self.base_rows.append(DexRow(i, box.name, dex_class, db.get(poke_id)))

        def add_form_box(box_name: str, ids: List[str]):
            self.boxes.add_box(box_name, ids)
            for i, poke_id in enumerate(ids):
                form_to_box[poke_id] = box_name

        # National Dex
        while not self.boxes.dex_finished():
            add_base_box(self.boxes.add_base_box(), DexClassification.NATIONAL)

        # Regionals
        for region in REGIONALS:
            add_base_box(self.boxes.add_box(region, db.regionals[region]), DexClassification.REGIONAL)

        # Special Forms
        for index, forms in enumerate(FORM_BOXES):
            add_form_box(f"Forms ({index + 1})", db.get_forms(forms))

        add_form_box("Unown", db.species_map["Unown"])
        add_form_box("Vivillon", db.species_map["Vivillon"])
        add_form_box("Alcremie", db.species_map["Alcremie"])

        for row in db.rows:
            if row.id in form_to_box:
                box_name = form_to_box[row.id]
                self.form_rows.append(DexRow(-1, box_name, DexClassification.FORMS, row))

    def write(self):
        rows = self.base_rows + self.form_rows
        out_rows: List[List[str]] = [row.to_dex_row(self.sheet) for row in rows]
        to_tsv(DEX_OUTFILE, out_rows)
