from enum import Enum

from main.constants.sheet_id import GENSHIN_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

SPREADSHEET_ID = GENSHIN_ID


CHARACTER_NAME_FIELD = "Character"


ABYSS_RANDOMIZE_CHARACTERS = {
    9: 2,
    10: 2,
    11: 2,
    12: 0,
}

ACHIEVEMENT_END = "You reached the end of your (achievement) journey ---- so far. Hehe!"


class AchievementFields(str, Enum):
    NAME = "Achievement"
    DESCRIPTION = "Description"
    NOTES = "Notes"
    CATEGORY = "Category"
    VERSION = "Version"
    PLAYER_1_MAIN = "L2"
    PLAYER_2_MAIN = "M2"
    PLAYER_3_MAIN = "P2"


class AchievementSections(str, Enum):
    WONDERS = "Wonders of the World"
    MEMORIES = "Memories of the Heart"
    NAMECARD = "N/A"


class AchievementCategories(str, Enum):
    HANGOUT = "Hangout"
    EXPLORATION = "Exploration"


class CharacterFields(str, Enum):
    NAME = "Character"
    BOSS_MATERIAL = "Boss Material"
    ENEMY_MATERIAL = "Enemy Material"
    LOCAL_SPECIALTY = "Local Specialty"
    TALENT_BOOK = "Talent Book"
    TROUNCE_TALENT = "Trounce Talent"
    RECIPE = "Recipe"


class Tab(str, Enum):
    CHARACTER_DATA = "Character Data"
    L_CHARS = "L Chars"
    ACHIEVEMENTS = "Achievements"
    TROUNCES = "Talent Trounces"
    RECIPES = "Recipes"
    TALENTS = "Talent Books"
    BOSS_DROPS = "Boss Drops"
    ENEMY_DROPS = "Enemy Drops"
    LOCALS = "Locals"


def get_sheet(tab_name: Tab) -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, tab_name.value)
    )
