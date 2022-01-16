from enum import Enum

from typing import List


def get_level_name(mode: str, chapter: str) -> str:
    return mode + " - " + chapter


class Mode(Enum):
    A_SIDE = 'A-Side'
    B_SIDE = 'B-Side'
    C_SIDE = 'C-Side'
    FULL_CLEAR = 'Full Clear'
    ANY_SPLIT = 'Any% Split'
    FAREWELL = 'Farewell'
    FULL_RUN = 'Full Run'
    BEST_POSSIBLE = 'Best Possible'

    def get_level(self, chapter: Enum):
        return get_level_name(self.value, chapter.value)


class Chapter(Enum):
    FORSAKEN_CITY = 'Forsaken City'
    OLD_SITE = 'Old Site'
    CELESTIAL_RESORT = 'Celestial Resort'
    GOLDEN_RIDGE = 'Golden Ridge'
    MIRROR_TEMPLE = 'Mirror Temple'
    REFLECTION = 'Reflection'
    THE_SUMMIT = 'The Summit'
    CORE = 'Core'


class FullRun(Enum):
    ANY_SPLIT = 'Any% Split'
    ANY_PERCENT = 'Any%'
    HUNDRED_MINUS = '100%-'
    FULL_HUNDRED = '100%'


MODES = list(Mode)
CHAPTERS = list(Chapter)


ANY_PERCENT_LEVELS: List[str] = [
    Mode.A_SIDE.get_level(chapter)
    for chapter in CHAPTERS if chapter != Chapter.CORE
]
