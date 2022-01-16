from main.util.time import millis_to_string, string_to_millis


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

    def add(self, score: Score):
        self.speed_total += score.get_speed_millis()
        self.death_total += score.get_deaths()

    def get(self) -> Score:
        return Score(millis_to_string(self.speed_total), str(self.death_total))
