from enum import Enum

from main.constants.sheet_id import GENSHIN_ID
from main.util.data import Sheet
from main.util.sheets import get_sheet_data

SPREADSHEET_ID = GENSHIN_ID

ACHIEVEMENTS_TAB = "Achievements"

ACHIEVEMENT_END = "You reached the end of your (achievement) journey ---- so far. Hehe!"


class AchievementFields(str, Enum):
    NAME = "Achievement"
    VERSION = "Version"
    PLAYER_1_MAIN = "L2"


class AchievementCategories(str, Enum):
    WONDERS = "Wonders of the World"
    MEMORIES = "Memories of the Heart"


def get_achievements_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, ACHIEVEMENTS_TAB)
    )
