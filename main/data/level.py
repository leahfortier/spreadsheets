from enum import Enum

from typing import List, Dict


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
    BEST_POSSIBLE = 'Best Possible*'

    def get_level(self, chapter: Enum):
        return get_level_name(self.value, chapter.value)

    def get_any_percent_levels(self) -> List[str]:
        return [
            self.get_level(chapter)
            for chapter in ANY_PERCENT_CHAPTERS
        ]

    def get_all_levels(self) -> List[str]:
        return [
            self.get_level(chapter)
            for chapter in CHAPTERS
        ]


class Chapter(Enum):
    FORSAKEN_CITY = 'Forsaken City'
    OLD_SITE = 'Old Site'
    CELESTIAL_RESORT = 'Celestial Resort'
    GOLDEN_RIDGE = 'Golden Ridge'
    MIRROR_TEMPLE = 'Mirror Temple'
    REFLECTION = 'Reflection'
    THE_SUMMIT = 'The Summit'
    CORE = 'Core'


class FarewellChapter(Enum):
    CLEAR = 'Clear'
    MOON_BERRY = 'Moon Berry'


class FullRun(Enum):
    ANY_SPLIT = 'Any% Split'
    ANY_PERCENT = 'Any%'
    HUNDRED_MINUS = '100%-'
    FULL_HUNDRED = '100%'

    def get_levels(self) -> List[str]:
        return _FULL_RUN_MAP[self]


CHAPTERS: List[Chapter] = list(Chapter)
FULL_RUNS: List[FullRun] = list(FullRun)

ANY_PERCENT_CHAPTERS: List[Chapter] = [chapter for chapter in CHAPTERS if chapter != Chapter.CORE]

_HUNDRED_MINUS_LEVELS: List[str] = Mode.FULL_CLEAR.get_all_levels() \
                                   + Mode.B_SIDE.get_all_levels() \
                                   + Mode.C_SIDE.get_all_levels()
_MOON_BERRY: str = Mode.FAREWELL.get_level(FarewellChapter.MOON_BERRY)

_FULL_RUN_MAP: Dict[FullRun, List[str]] = {
    FullRun.ANY_SPLIT: Mode.ANY_SPLIT.get_any_percent_levels(),
    FullRun.ANY_PERCENT: Mode.A_SIDE.get_any_percent_levels(),
    FullRun.HUNDRED_MINUS: _HUNDRED_MINUS_LEVELS,
    FullRun.FULL_HUNDRED: _HUNDRED_MINUS_LEVELS + [_MOON_BERRY],
}
