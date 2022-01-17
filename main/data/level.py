from enum import Enum

from typing import List, Dict


class Level:
    def __init__(self, mode: str, chapter: str):
        self.mode = mode
        self.chapter = chapter

    def __str__(self):
        return self.name()

    def __eq__(self, other):
        return self.name() == other.name()

    def __hash__(self):
        return hash(self.name())

    def name(self) -> str:
        return self.mode + " - " + self.chapter


class Mode(Enum):
    A_SIDE = 'A-Side'
    B_SIDE = 'B-Side'
    C_SIDE = 'C-Side'
    FULL_CLEAR = 'Full Clear'
    ANY_SPLIT = 'Any% Split'
    FAREWELL = 'Farewell'
    FULL_RUN = 'Full Run'
    BEST_POSSIBLE = 'Best Possible*'

    def level(self, chapter: Enum) -> Level:
        return Level(self.value, chapter.value)

    def get_any_percent_levels(self) -> List[Level]:
        return [
            self.level(chapter)
            for chapter in ANY_PERCENT_CHAPTERS
        ]

    def get_all_levels(self) -> List[Level]:
        return [
            self.level(chapter)
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


class Farewell(Enum):
    CLEAR = 'Clear'
    MOON_BERRY = 'Moon Berry'


class FullRun(Enum):
    ANY_SPLIT = 'Any% Split'
    ANY_PERCENT = 'Any%'
    HUNDRED_MINUS = '100%-'
    FULL_HUNDRED = '100%'

    def get_levels(self) -> List[Level]:
        return _FULL_RUN_MAP[self]


MODES: List[Mode] = list(Mode)
CHAPTERS: List[Chapter] = list(Chapter)
FULL_RUNS: List[FullRun] = list(FullRun)

ANY_PERCENT_CHAPTERS: List[Chapter] = [chapter for chapter in CHAPTERS if chapter != Chapter.CORE]

_HUNDRED_MINUS_LEVELS: List[Level] = Mode.FULL_CLEAR.get_all_levels() \
                                   + Mode.B_SIDE.get_all_levels() \
                                   + Mode.C_SIDE.get_all_levels()

_FULL_RUN_MAP: Dict[FullRun, List[Level]] = {
    FullRun.ANY_SPLIT: Mode.ANY_SPLIT.get_any_percent_levels(),
    FullRun.ANY_PERCENT: Mode.A_SIDE.get_any_percent_levels(),
    FullRun.HUNDRED_MINUS: _HUNDRED_MINUS_LEVELS,
    FullRun.FULL_HUNDRED: _HUNDRED_MINUS_LEVELS + [Mode.FAREWELL.level(Farewell.MOON_BERRY)],
}
