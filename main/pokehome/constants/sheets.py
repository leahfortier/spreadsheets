from enum import Enum
from typing import List

from main.constants.sheet_id import POKEMON_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

SPREADSHEET_ID = POKEMON_ID

EMPTY_FIELD = "--"

DB_TAB = "Database"
DEX_TAB = "Live Dex"
DOKU_TAB = "Doku Dex"
GO_TAB = "GO Dex"


class SpriteType(str, Enum):
    NORMAL = "normal"
    SHINY = "shiny"


class DexClassification(str, Enum):
    NATIONAL = "National"
    REGIONAL = "Regional"
    FORMS = "Forms"


class HiddenAbilityProgress(str, Enum):
    OBTAINED = "Yes"
    UNOBTAINED = "No"
    NO_HIDDEN_ABILITY = "N/A"
    FAMILY_OBTAINED = "Family"
    GENDERED_NON_POKE_BALL = "Breed"


class EvolutionType(str, Enum):
    FIRST = "First"
    MIDDLE = "Middle"
    FINAL = "Final"
    NONE = "None"


class DokuFormType(str, Enum):
    BASE = "Base"
    ALT = "Alt"
    GENDER = "Gender"
    REGIONAL = "Regional"
    MEGA = "Mega"
    GMAX = "Gmax"


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
    DIGIMON_FORM = "digimon"
    REGIONAL_FORM = "regional"
    FORM = "form"
    GENDER_FORM = "gender"
    NAME = "name"
    IMAGE = "img"
    SHINY_IMAGE = "shiny"
    ABILITY1 = "ability1"
    ABILITY2 = "ability2"
    HIDDEN_ABILITY = "hidden"
    TYPE1 = "type1"
    TYPE2 = "type2"
    BRANCH_EVO = "branch evo"
    EVO_TYPE = "evolution"
    FAMILY_EVOS = "family"
    GENERATION = "generation"
    OG_REGION = "og region"
    GENDER_RATIO = "gender ratio"
    CAN_BREED = "can breed"
    CATCH_RATE = "catch rate"


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


class DokuFields(str, Enum):
    ID = "Id"
    NAME = "Name"
    IMAGE = "Image"
    DEX = "Dex"
    SHINY = "Shiny"
    GENERATION = "Gen"
    REGION = "Region"
    TYPE1 = "Type 1"
    TYPE2 = "Type 2"
    BRANCH_EVO = "Branch"
    FORM = "Form"
    EVO_TYPE = "Evolution"


class GoFields(str, Enum):
    ID = "Id"
    NAME = "Name"
    REGION = "Region"
    IMAGE = "Image"


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


def get_doku_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, DOKU_TAB),
        escape_fields=[DokuFields.ID],
        id_fields=[DokuFields.ID]
    )


def get_go_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, GO_TAB),
        escape_fields=[GoFields.ID],
        id_fields=[GoFields.ID]
    )
