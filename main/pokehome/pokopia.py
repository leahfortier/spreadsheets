from typing import List, Dict

from main.pokehome.constants.io import DB_OUTFILE, PK_ITEMS_OUTFILE
from main.pokehome.constants.sheets import PokopiaFields, get_pokopia_sheet
from main.util.data import Sheet
from main.util.file_io import to_tsv
from util.sheets_formulas import image
from util.warn import GuardDog

guard = GuardDog()


class ItemRow:
    def __init__(self, sheet: Sheet, row: List[str], row_index: int, class_counts: Dict[str, int]):
        self.classification = sheet.get(row, PokopiaFields.CLASS)
        cat_index = class_counts.get(self.classification, 0)
        class_counts[self.classification] = cat_index + 1

        sheet.set(row, PokopiaFields.SORT_ID, str(row_index + 1))
        sheet.update(row, PokopiaFields.ALL_ROW, str(row_index // 12 + 1))
        sheet.update(row, PokopiaFields.ALL_COL, str(row_index % 12 + 1))
        sheet.update(row, PokopiaFields.CAT_ROW, str(cat_index // 12 + 1))
        sheet.update(row, PokopiaFields.CAT_COL, str(cat_index % 12 + 1))

        self.name = sheet.get(row, PokopiaFields.NAME)
        name_field = sheet.column_field(PokopiaFields.NAME, row_index)

        self.image_id = f'=SUBSTITUTE(SUBSTITUTE(LOWER({name_field}), "é", "e"), " ", "")'

        self.image = image(self.get_image_url())
        sheet.set(row, PokopiaFields.IMAGE, self.image)

    # Get the id in the format that serebii uses
    # Go to https://www.serebii.net/pokemonpokopia/items.shtml if not appearing correctly
    def get_image_url(self) -> str:
        image_id = self.name.lower().replace("é", "e").replace(" ", "")

        if image_id == "???":
            return "https://archives.bulbagarden.net/media/upload/1/1a/Spr_3e_000.png"
        return f'https://www.serebii.net/pokemonpokopia/items/{image_id}.png'


class Pokopia:
    def __init__(self):
        self.sheet: Sheet = get_pokopia_sheet()
        class_count: Dict[str, int] = {}
        self.rows: List[ItemRow] = [
            ItemRow(self.sheet, row, index, class_count)
            for index, row in enumerate(self.sheet.rows)
        ]

    def write(self):
        to_tsv(PK_ITEMS_OUTFILE, [row for row in self.sheet.rows], show_diff=False)

