from enum import Enum
from typing import List

from main.constants.sheet_id import POKEMON_ID
from main.util.data import Sheet
from main.util.sheets import get_sheet_data


SPREADSHEET_ID = POKEMON_ID

EMPTY_ABILITY = "--"

DB_TAB = "Database"
DEX_TAB = "Live Dex"


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


class DbFields(str, Enum):
    DEX = "dex"
    FORM_ID = "form id"
    GENDER_ID = "gender id"
    ID = "id"
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
