from typing import Dict, List, Iterable

from main.data.level import Level
from main.data.score import Score, ScoreCounter


class Records:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.level_map: Dict[Level, Score] = {}

    def add_record(self, mode: str, chapter: str, speed: str, death: str) -> None:
        self.level_map[Level(mode, chapter)] = Score(speed, death)

    def levels(self) -> Iterable[Level]:
        return self.level_map.keys()

    def get(self, level: Level) -> Score:
        if level not in self.level_map:
            print(f'Level "{level}" not in map.')

        return self.level_map[level]

    def get_best_possible(self, levels: List[Level]) -> Score:
        counter: ScoreCounter = ScoreCounter()
        for level in levels:
            counter.add(self.get(level))
        return counter.get()




