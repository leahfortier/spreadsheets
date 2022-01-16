from datetime import date
from typing import List

from main.data.score import Score
from main.util.file_io import from_csv, from_file, to_file
from main.data.records import Records
from main.data.scoreboard import Scoreboard
from main.util.constants import PREVIOUS_FILE, DIFFS_FILE


class Diff:
    def __init__(self, player_name: str, level: str, old: str, new: str):
        self.today: str = date.today().strftime("%m/%d/%y")
        self.player_name = player_name
        self.level = level
        self.old = old
        self.new = new

    def __str__(self):
        return f'{self.today}' \
               f'\t{self.player_name:10}' \
               f'\t{self.level:30}' \
               f'\t{self.old} -> {self.new}'


def add_diff(diffs: List[Diff], player_name: str, level: str, old: str, new: str):
    if old != new:
        diffs.append(Diff(player_name, level, old, new))


def records_diff(player_name: str, old: Records, new: Records) -> List[Diff]:
    diffs: List[Diff] = []
    for level in old.levels():
        old_score: Score = old.get(level)
        new_score: Score = new.get(level)
        add_diff(diffs, player_name, level, old_score.speed, new_score.speed)
        add_diff(diffs, player_name, level, old_score.deaths, new_score.deaths)
    return diffs


def board_diff(old: Scoreboard, new: Scoreboard) -> List[Diff]:
    diffs: List[Diff] = []
    for player_name in old.players():
        first_records = old.get(player_name)
        second_records = new.get(player_name)
        diffs += records_diff(player_name, first_records, second_records)
    return diffs


def check_diffs(new_board: Scoreboard):
    previous_times: List[List[str]] = from_csv(PREVIOUS_FILE)
    old_board: Scoreboard = Scoreboard(new_board.players(), previous_times)

    prev_diffs: List[str] = from_file(DIFFS_FILE)
    new_diffs: List[str] = [str(diffy) for diffy in board_diff(old_board, new_board)]

    if len(new_diffs) == 0:
        print("No diffs.")
    else:
        print("Diffs:")
        for diffy in new_diffs:
            print("\t" + diffy)

    to_file(DIFFS_FILE, prev_diffs + new_diffs)