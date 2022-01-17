from enum import Enum, auto

from main.util.time import millis_to_string, string_to_millis


class ScoreType(Enum):
    SPEED = 'Speed'
    DEATH = 'Death'


class Score:
    def __init__(self, speed: str, deaths: str):
        self.speed: str = speed
        self.deaths: str = deaths

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
        if self.invalid or score.speed == '--' or score.deaths == '--':
            self.invalid = True
        else:
            self.speed_total += score.get_speed_millis()
            self.death_total += score.get_deaths()

    def get(self) -> Score:
        if self.invalid:
            return Score('--', '--')
        return Score(millis_to_string(self.speed_total), str(self.death_total))
