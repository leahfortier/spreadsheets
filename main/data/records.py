from enum import Enum
from typing import Dict, List, Iterable

from main.data.level import get_level_name, Mode, Chapter, CHAPTERS, Score, ScoreCounter


class Records:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.level_map: Dict[str, Score] = {}

    def add_record(self, mode: str, chapter: str, speed: str, death: str) -> None:
        self.level_map[get_level_name(mode, chapter)] = Score(speed, death)

    def levels(self) -> Iterable[str]:
        return self.level_map.keys()

    def get(self, level: str) -> Score:
        if level not in self.level_map:
            print(f'Level "{level}" not in map.')

        return self.level_map[level]

    def get_best_possible(self, levels: List[str]) -> Score:
        counter: ScoreCounter = ScoreCounter()
        for level in levels:
            counter.add(self.get(level))
        return counter.get()




