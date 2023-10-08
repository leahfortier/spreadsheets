from typing import List, Dict

from main.pokehome.constants.io import DB_OUTFILE
from main.pokehome.constants.pokes import INCLUDE_GENDER_FORM, EXCLUDE_BASE_FORM
from main.pokehome.constants.sheets import DbFields, get_db_sheet, SpriteType
from main.util.data import Sheet
from main.util.file_io import to_tsv
from main.util.general import remove_suffix


class DbRow:
    def __init__(self, sheet: Sheet, row: List[str], row_index: int):
        sheet.update(row, DbFields.SORT_ID, str(row_index + 1))

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

        self.image_id = self.get_image_id()
        sheet.update(row, DbFields.IMAGE_ID, self.image_id)

        shiny_id = self.image_id
        if self.species == "Minior":
            # All Minior cores have the same shiny
            shiny_id = self.get_image_id("core")

        def get_image_url(sprite_type: SpriteType, image_id: str) -> str:
            return f'=image("https://img.pokemondb.net/sprites/home/{sprite_type}/1x/{image_id}.png")'

        self.image = get_image_url(SpriteType.NORMAL, self.image_id)
        self.shiny_image = get_image_url(SpriteType.SHINY, shiny_id)

        sheet.set(row, DbFields.IMAGE, self.image)
        sheet.set(row, DbFields.SHINY_IMAGE, self.shiny_image)

    # Get the id in the format that pokemondb uses
    # Go to https://pokemondb.net/sprites/<species_name> and look at the different
    #   forms under "Home" if form is not appearing correctly
    def get_image_id(self, image_form_id: str = "") -> str:
        image_form_id = image_form_id or self.form or self.regional_form

        image_form_id = remove_suffix(image_form_id, [" Sea", " Flower", " Style"])
        if self.species == "Darmanitan":
            image_form_id += "-standard"
        elif self.species in ["Sinistea", "Polteageist"]:
            # Sinistea/Polteageist do not have separate sprites for their antique forms
            image_form_id = ""

        if self.species in ["Meowstic", "Alcremie", "Indeedee", "Basculegion", "Oinkologne"]:
            image_form_id += "-" + self.gender_form
        else:
            image_form_id += self.gender_id

        image_id = "-".join(filter(None, [self.species, image_form_id])).lower() \
            .replace("♂", "-m").replace("♀", "-f") \
            .replace(" of three", "3").replace(" of four", "4") \
            .replace("'", "").replace(".", "") \
            .replace("%", "").replace(":", "") \
            .replace("é", "e").replace("?", "qm").replace("!", "em") \
            .replace(" ", "-").replace("--", "-")

        return image_id

    def is_base_form(self, regional_is_base=False) -> bool:
        if self.id == self.dex:
            return True
        if self.gender_id:
            return False
        if self.form:
            return False
        if regional_is_base and self.regional_form:
            return True
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
        self.rows: List[DbRow] = [
            DbRow(self.sheet, row, index)
            for index, row in enumerate(self.sheet.rows)
        ]

        self.id_map: Dict[str, int] = {}
        self.species_map: Dict[str, List[str]] = {}
        self.regionals: Dict[str, List[str]] = {}

        for index, row in enumerate(self.rows):
            assert row.id not in self.id_map
            self.id_map[row.id] = index

            self.species_map.setdefault(row.species, []).append(row.id)
            if row.regional_form and row.is_base_form(regional_is_base=True):
                self.regionals.setdefault(row.regional_form, []).append(row.id)

    def get(self, poke_id: str) -> DbRow:
        return self.rows[self.id_map[poke_id]]

    def get_forms(self, names: List[str], regional_is_alt=False) -> List[str]:
        forms: List[str] = []
        for name in names:
            for poke_id in self.species_map.get(name):
                row: DbRow = self.get(poke_id)
                if row.is_alt_form(regional_is_alt=regional_is_alt):
                    forms.append(poke_id)
        return forms

    def write(self):
        to_tsv(DB_OUTFILE, [row for row in self.sheet.rows])

