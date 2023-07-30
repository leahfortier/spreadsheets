from enum import Enum, auto

from typing import List

from main.celeste.constants import EMPTY_FIELD
from main.util.time import millis_to_string, string_to_millis


class ScoreType(Enum):
    SPEED = 'Speed'
    DEATH = 'Deaths'


SCORE_TYPES: List[ScoreType] = list(ScoreType)


def get_score_type(value: str) -> ScoreType:
    for score_type in SCORE_TYPES:
        if score_type.value == value:
            return score_type
    print(f'Unknown score type {value}')


class Score:
    def __init__(self, speed: str, deaths: str):
        self.speed: str = speed
        self.deaths: str = deaths

    def __str__(self):
        return f'{self.speed} {self.deaths}'

    def get(self, score_type: ScoreType) -> str:
        if score_type == ScoreType.SPEED:
            return self.speed
        if score_type == ScoreType.DEATH:
            return self.deaths

    def get_value(self, score_type: ScoreType) -> int:
        if score_type == ScoreType.SPEED:
            return self.get_speed_millis()
        if score_type == ScoreType.DEATH:
            return self.get_deaths()

    def get_deaths(self) -> int:
        return int(self.deaths)

    def get_speed_millis(self) -> int:
        return string_to_millis(self.speed)


class ScoreCounter:
    def __init__(self):
        self.speed_total: int = 0
        self.death_total: int = 0
        self.invalid: bool = False

    def add(self, score: Score) -> None:
        if self.invalid or score.speed == EMPTY_FIELD or score.deaths == EMPTY_FIELD:
            self.invalid = True
        else:
            self.speed_total += score.get_speed_millis()
            self.death_total += score.get_deaths()

    def get(self) -> Score:
        if self.invalid:
            return Score(EMPTY_FIELD, EMPTY_FIELD)
        return Score(millis_to_string(self.speed_total), str(self.death_total))
