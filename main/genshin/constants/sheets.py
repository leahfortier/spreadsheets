from enum import Enum

from main.constants.sheet_id import GENSHIN_ID
from main.util.data import Sheet
from main.util.sheets import get_sheet_data

SPREADSHEET_ID = GENSHIN_ID

ACHIEVEMENTS_TAB = "Achievements"


class AchievementFields(str, Enum):
    NAME = "Achievement"
    VERSION = "Version"


def get_achievements_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(SPREADSHEET_ID, ACHIEVEMENTS_TAB)
    )
