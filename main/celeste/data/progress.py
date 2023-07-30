from typing import List, Dict

from main.celeste.analysis.diffs import Diff
from main.celeste.data.level import Level
from main.celeste.data.score import Score, ScoreType
from main.celeste.constants import DEFAULT_DATE


class Event:
    def __init__(self, value: str, date: str = None):
        self.date: str = date or DEFAULT_DATE
        self.value = value

    def __str__(self):
        return f'{self.date} {self.value}'


class Progress:
    def __init__(self, current: str):
        self.events: List[Event] = [Event(current)]

    def add(self, date: str, previous: str, current: str):
        if self.events[-1].value != current:
            event_str: List[str] = [str(event) for event in self.events]
            print(f'Gaps in progress for {date}, {previous} -> {current}: {event_str}')
        self.events[-1].date = date
        self.events.append(Event(previous))


class ProgressMap:
    def __init__(self):
        self.progress: Dict[str, Progress] = {}

    @classmethod
    def key(cls, player_name: str, level: Level, score_type: ScoreType):
        return f'{player_name}~{level.name()}~{score_type.name}'

    def get(self, player_name: str, level: Level, score_type: ScoreType) -> Progress:
        key = self.key(player_name, level, score_type)
        if key not in self.progress:
            print(f'Key {key} not in progress map.')
        return self.progress[key]

    def add_event(self, diffy: Diff):
        self.get(diffy.player_name, diffy.level, diffy.type).add(diffy.date, diffy.old, diffy.new)

    def add_score(self, player_name: str, level: Level, score: Score):
        self.progress[self.key(player_name, level, ScoreType.SPEED)] = Progress(score.speed)
        self.progress[self.key(player_name, level, ScoreType.DEATH)] = Progress(score.deaths)
