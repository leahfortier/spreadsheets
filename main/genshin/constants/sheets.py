from enum import Enum

from main.constants.sheet_id import GENSHIN_ID
from main.util.data import Sheet
from main.util.sheets_parse import get_sheet_data

SPREADSHEET_ID = GENSHIN_ID

ACHIEVEMENTS_TAB = "Achievements"

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


def get_achievements_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, ACHIEVEMENTS_TAB)
    )
