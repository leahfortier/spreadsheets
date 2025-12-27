from enum import Enum
from typing import List

from main.constants.sheet_id import GENSHIN_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

SPREADSHEET_ID = GENSHIN_ID

NUM_TRAVELERS = 6


class BuildsFields(str, Enum):
    NAME = "Character"
    CONSTELLATION = "C"
    CHAR_LEVEL = "Lvl"
    NORMAL_TALENT = "N"
    SKILL_TALENT = "Skill"
    BURST_TALENT = "Brst"
    WEAPON = "Weapon"
    WEAPON_STAT = "Stat"
    WEAPON_METHOD = "Method"
    WEAPON_RARITY = "★"
    WEAPON_LEVEL = "Lv."
    WEAPON_RANK = "R"
    CHAR_SORT = "Char. Sort"
    USE_SORT = "Use Sort"


BUILD_SORT_FIELDS: List[BuildsFields] = [BuildsFields.CHAR_SORT, BuildsFields.USE_SORT]


class WeaponMethod(str, Enum):
    STANDARD = "Standard"
    LIMITED_BANNER = "Banner"
    BATTLE_PASS = "BP"
    EVENT = "Event"
    SIGNATURE = "Signature"
    FISH = "Fish"
    FORGE = "Craft"


ABYSS_RANDOMIZE_CHARACTERS = {
    9: 2,
    10: 2,
    11: 2,
    12: 0,
}

ACHIEVEMENT_END = "You reached the end of your (achievement) journey ---- so far. Hehe!"


# First field is required, others are optional for achievements with multiple levels
PLAYER_FIELDS = [
    ["L2", "L1", "L3"],
    ["M2", "M1", "M3"],
    ["P2", "P1", "P3"],
]


class AchievementFields(str, Enum):
    ACHIEVEMENT = "Achievement"
    DESCRIPTION = "Description"
    NOTES = "Notes"
    CATEGORY = "Category"
    VERSION = "Version"
    PLAYER_MAIN = PLAYER_FIELDS[0][0],


class AchievementSections(str, Enum):
    WONDERS = "Wonders of the World"
    MEMORIES = "Memories of the Heart"
    NAMECARD = "N/A"


class AchievementCategories(str, Enum):
    HANGOUT = "Hangout"
    EXPLORATION = "Exploration"


class CharacterFields(str, Enum):
    NAME = "Character"
    WEAPON = "Weapon"
    VERSION = "Version"
    BOSS_MATERIAL = "Boss Material"
    ENEMY_MATERIAL = "Enemy Material"
    LOCAL_SPECIALTY = "Local Specialty"
    TALENT_BOOK = "Talent Book"
    TROUNCE_TALENT = "Trounce Talent"
    RECIPE = "Recipe"


class Tab(str, Enum):
    CHARACTER_DATA = "Character Data"
    L_CHARS = "L Builds"
    MEL_CHARS = "Mel Builds"
    ACHIEVEMENTS = "Achievements"
    TROUNCES = "Talent Trounces"
    RECIPES = "Recipes"
    TALENTS = "Talent Books"
    BOSS_DROPS = "Boss Drops"
    ENEMY_DROPS = "Enemy Drops"
    LOCALS = "Locals"


BUILD_TABS: List[Tab] = [
    Tab.L_CHARS,
    Tab.MEL_CHARS,
]


def get_sheet(tab_name: Tab) -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, tab_name.value)
    )
