from typing import Dict, Iterable, List

from main.celeste.data.level import Level
from main.celeste.data.score import Score, ScoreCounter


class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.records: Dict[Level, Score] = {}

    def add_record(self, mode: str, chapter: str, speed: str, death: str) -> None:
        level: Level = Level(mode, chapter)
        self.records[level] = Score(speed, death)

    def levels(self) -> Iterable[Level]:
        return self.records.keys()

    def get(self, level: Level) -> Score:
        if level not in self.records:
            print(f'Level "{level}" not in map.')

        return self.records[level]

    def get_best_possible(self, levels: List[Level]) -> Score:
        counter: ScoreCounter = ScoreCounter()
        for level in levels:
            counter.add(self.get(level))
        return counter.get()
