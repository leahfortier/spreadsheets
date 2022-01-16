from main.data.level import Score, Mode, FullRun, ANY_PERCENT_LEVELS
from main.data.records import Records
from main.data.scoreboard import Scoreboard


def print_update(player_name: str, old: str, new: str) -> None:
    if old != new:
        print(f'UPDATE ANY% BEST: {player_name}: {old} -> {new}')


def best_possible(board: Scoreboard):
    for player_name in board.players():
        records: Records = board.get(player_name)
        current_best: Score = records.get_best_possible(ANY_PERCENT_LEVELS)
        previous_best: Score = records.get(Mode.BEST_POSSIBLE.get_level(FullRun.ANY_PERCENT))
        print_update(player_name, previous_best.speed, current_best.speed)
        print_update(player_name, previous_best.deaths, current_best.deaths)
