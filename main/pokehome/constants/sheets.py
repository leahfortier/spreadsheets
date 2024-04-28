from enum import Enum
from typing import List

from main.constants.sheet_id import POKEMON_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

SPREADSHEET_ID = POKEMON_ID

EMPTY_ABILITY = "--"

DB_TAB = "Database"
DEX_TAB = "Live Dex"


class SpriteType(str, Enum):
    NORMAL = "normal"
    SHINY = "shiny"


class DexClassification(str, Enum):
    NATIONAL = "National",
    REGIONAL = "Regional",
    FORMS = "Forms"


class HiddenAbilityProgress(str, Enum):
    OBTAINED = "Yes"
    UNOBTAINED = "No"
    NO_HIDDEN_ABILITY = "N/A"
    FAMILY_OBTAINED = "Family"
    GENDERED_NON_POKE_BALL = "Breed"


class GenderRatio(str, Enum):
    MALE_ONLY = "100% Male"
    EIGHTH_FEMALE = "12.5% Female"
    FOURTH_FEMALE = "25% Female"
    EQUAL = "50% Female"
    FOURTH_MALE = "75% Female"
    EIGHTH_MALE = "87.5% Female"
    FEMALE_ONLY = "100% Female"
    GENDERLESS = "Genderless"


class DbFields(str, Enum):
    SORT_ID = "sort"
    DEX = "dex"
    FORM_ID = "form id"
    GENDER_ID = "gender id"
    ID = "id"
    IMAGE_ID = "img id"
    SPECIES = "species"
    REGIONAL_FORM = "regional"
    FORM = "form"
    GENDER_FORM = "gender"
    NAME = "name"
    IMAGE = "img"
    SHINY_IMAGE = "shiny"
    ABILITY1 = "ability1"
    ABILITY2 = "ability2"
    HIDDEN_ABILITY = "hidden"
    FAMILY_EVOS = "family"
    OG_REGION = "og region"
    GENDER_RATIO = "gender ratio"
    CAN_BREED = "can breed"


class DexFields(str, Enum):
    BOX = "Box"
    ROW = "Row"
    COL = "Col"
    ID = "Id"
    NAME = "Name"
    IMAGE = "Image"
    SHINY_IMAGE = "Shiny Image"
    HIDDEN_ABILITY = "Hidden"
    NOTES = "Notes"
    NICKNAME = "Nickname"
    TRAINER = "OT"
    CAUGHT_PROGRESS = "Caught"
    HIDDEN_PROGRESS = "With Hidden"
    REGION = "Region"
    CLASS = "Class"
    SHINY = "Shiny"
    SIX_IV = "6IV"


SAME_ID_DIFFERENT_FIELDS: List[str] = [
    DexFields.CAUGHT_PROGRESS,
    DexFields.HIDDEN_PROGRESS,
    DexFields.ROW,
    DexFields.COL,
    DexFields.NICKNAME,
    DexFields.TRAINER,
    DexFields.NOTES,
    DexFields.CLASS,
]


def get_db_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, DB_TAB),
        escape_fields=[DbFields.ID, DbFields.DEX],
        id_fields=[DbFields.ID]
    )


def get_dex_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, DEX_TAB),
        escape_fields=[DexFields.ID],
        id_fields=[DexFields.ID, DexFields.BOX]
    )
