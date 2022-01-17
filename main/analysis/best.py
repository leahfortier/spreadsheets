from main.data.level import Mode, FullRun, FULL_RUNS
from main.data.player import Player
from main.data.score import Score
from main.data.scoreboard import Scoreboard


def print_update(title: str, player_name: str, old: str, new: str) -> None:
    if old != new:
        print(f'Update {title} Best Possible: {player_name}: {old} -> {new}')


def check_updates(title: str, player_name: str, old: Score, new: Score) -> None:
    print_update(title, player_name, old.speed, new.speed)
    print_update(title, player_name, old.deaths, new.deaths)


def best_possible(board: Scoreboard):
    for player_name in board.players():
        player: Player = board.get(player_name)
        for full_run in FULL_RUNS:
            check_updates(
                full_run.value,
                player_name,
                player.get(Mode.BEST_POSSIBLE.level(full_run)),
                player.get_best_possible(full_run.get_levels())
            )
