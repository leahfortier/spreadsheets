from typing import List, Dict

from main.pokehome.constants.io import DB_OUTFILE
from main.pokehome.constants.pokes import INCLUDE_GENDER_FORM, EXCLUDE_BASE_FORM, DIGIMON, NON_HOME_FORMS
from main.pokehome.constants.sheets import DbFields, get_db_sheet, SpriteType, DB_TRUE
from main.util.data import Sheet
from main.util.file_io import to_tsv
from main.util.general import remove_suffix, has_prefix, remove_prefix
from util.sheets_formulas import image


class DbRow:
    def __init__(self, sheet: Sheet, row: List[str], row_index: int):
        sheet.update(row, DbFields.SORT_ID, str(row_index + 1), print_diff=False)

        self.dex = sheet.get(row, DbFields.DEX)
        self.form_id = sheet.get(row, DbFields.FORM_ID)
        self.gender_id = sheet.get(row, DbFields.GENDER_ID)

        self.species = sheet.get(row, DbFields.SPECIES)
        self.digimon_form = sheet.get(row, DbFields.DIGIMON_FORM)
        self.regional_form = sheet.get(row, DbFields.REGIONAL_FORM)
        self.form = sheet.get(row, DbFields.FORM)
        self.gender_form = sheet.get(row, DbFields.GENDER_FORM)

        self.ability1 = sheet.get(row, DbFields.ABILITY1)
        self.ability2 = sheet.get(row, DbFields.ABILITY2)
        self.hidden = sheet.get(row, DbFields.HIDDEN_ABILITY)

        self.type1 = sheet.get(row, DbFields.TYPE1)
        self.type2 = sheet.get(row, DbFields.TYPE2)

        self.generation = sheet.get(row, DbFields.GENERATION)
        self.region = sheet.get(row, DbFields.OG_REGION)

        self.catch_rate = sheet.get(row, DbFields.CATCH_RATE)
        self.can_breed_field = sheet.get(row, DbFields.CAN_BREED)
        self.gender_ratio = sheet.get(row, DbFields.GENDER_RATIO)

        self.has_branch_evo = sheet.get(row, DbFields.HAS_BRANCH)
        self.evolution_type = sheet.get(row, DbFields.EVO_TYPE)
        self.family = sheet.get(row, DbFields.FAMILY_EVOS)

        self.baby = sheet.get(row, DbFields.IS_BABY)
        self.fossil = sheet.get(row, DbFields.IS_FOSSIL)
        self.partner = sheet.get(row, DbFields.IS_PARTNER)
        self.legendary = sheet.get(row, DbFields.IS_LEGENDARY)
        self.mythical = sheet.get(row, DbFields.IS_MYTHICAL)
        self.paradox = sheet.get(row, DbFields.IS_PARADOX)
        self.ultra = sheet.get(row, DbFields.IS_ULTRA_BEAST)

        self.id = self.dex + self.form_id + self.gender_id
        sheet.update(row, DbFields.ID, self.id)

        name_form = self.form
        digimon_form = self.digimon_form
        if self.species == "Alcremie" and self.gender_form:
            name_form += " - " + self.gender_form
        if name_form:
            name_form = f"({name_form})"
        if digimon_form:
            assert has_prefix(digimon_form, DIGIMON)
            # Ex: This would be the "X" of "Mega X"
            digimon_variant = remove_prefix(digimon_form, DIGIMON).strip()
            assert not (name_form and digimon_variant)  # Can add support for this if it comes up
            if digimon_variant:
                digimon_form = remove_suffix(digimon_form, [" " + digimon_variant])
                name_form = digimon_variant

        self.name = " ".join(filter(None, [digimon_form, self.regional_form, self.species, name_form]))
        sheet.update(row, DbFields.NAME, self.name)

        self.image_id = self.get_image_id()
        sheet.update(row, DbFields.IMAGE_ID, self.image_id)

        self.image = image(self.get_image_url(SpriteType.NORMAL))
        self.shiny_image = image(self.get_image_url(SpriteType.SHINY))

        sheet.set(row, DbFields.IMAGE, self.image)
        sheet.set(row, DbFields.SHINY_IMAGE, self.shiny_image)

    # Get the id in the format that pokemondb uses
    # Go to https://pokemondb.net/sprites/<species_name> and look at the different
    #   forms under "Home" if form is not appearing correctly
    def get_image_id(self, image_form_id: str = "") -> str:
        form_name = remove_suffix(
            self.form,
            [
                " Form", " Sea", " Flower",
                " Style", " Mask", " Mode",
                " Face"
            ]
        )
        if self.species == "Darmanitan":
            if not form_name:
                form_name = "Standard"
            # Darmanitan is the only regional with a variant that includes the regional name in the id
            if self.regional_form:
                form_name = self.regional_form + "-" + form_name
        elif self.species in ["Sinistea", "Polteageist"]:
            # Sinistea/Polteageist do not have separate sprites for their antique forms
            form_name = ""
        elif self.species == "Toxtricity" and self.digimon_form:
            # Amped and Low Key Gigantamax images are the same
            form_name = ""

        suffix = self.digimon_form
        if self.digimon_form == "Partner":
            # These don't currently have unique sprites
            suffix = ""

        if not image_form_id:
            image_form_id = "-".join(filter(None, [form_name or self.regional_form, suffix]))

        if self.gender_form and self.species in ["Meowstic", "Alcremie", "Indeedee", "Basculegion", "Oinkologne"]:
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

    def get_image_url(self, sprite_type: SpriteType) -> str:
        image_id = self.image_id
        if sprite_type == SpriteType.SHINY and self.species == "Minior":
            # All Minior cores have the same shiny
            image_id = self.get_image_id("core")

        if self.name == "Cowboy Caterpie":
            return "https://pokedoku-space.nyc3.cdn.digitaloceanspaces.com/resources/pokemon/99901.png"
        if self.name == "Floette (Eternal Flower)":
            return f'https://img.pokemondb.net/sprites/bank/{sprite_type.value}/{image_id}.png'
        return f'https://img.pokemondb.net/sprites/home/{sprite_type.value}/1x/{image_id}.png'

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
        if self.species in NON_HOME_FORMS and self.form in NON_HOME_FORMS[self.species]:
            return False
        if self.digimon_form:
            return False
        if self.gender_id:
            return self.species in INCLUDE_GENDER_FORM
        if self.form:
            return True
        if regional_is_alt and self.regional_form:
            return True
        return False

    def can_breed(self):
        return self.can_breed_field == DB_TRUE

    def is_baby(self):
        return self.baby == DB_TRUE

    def is_fossil(self):
        return self.fossil == DB_TRUE

    def regional_name(self):
        if self.regional_form:
            return self.regional_form + " " + self.species
        return self.species


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
            assert row.id not in self.id_map, f'{row.id} {row.name}'
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

