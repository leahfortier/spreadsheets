from datetime import date as datetime
from typing import List

from main.data.level import Level
from main.data.records import Records
from main.data.score import Score, ScoreType
from main.data.scoreboard import Scoreboard
from main.util.constants import PREVIOUS_FILE, DIFFS_FILE
from main.util.file_io import from_csv, from_file, to_file


class Diff:
    def __init__(self, player_name: str, level: Level, score_type: str, old: str, new: str, date: str = None):
        self.date: str = date or datetime.today().strftime("%m/%d/%y")
        self.player_name = player_name
        self.level = level
        self.type = score_type
        self.old = old
        self.new = new

    def csv_string(self):
        return ','.join([
            self.date,
            self.player_name,
            self.level.mode,
            self.level.chapter,
            self.type,
            self.old,
            self.new
        ])

    def __str__(self):
        return f'{self.date}' \
               f'\t{self.player_name:10}' \
               f'\t{self.level:30}' \
               f'\t{self.old:>12}' \
               f'\t{self.new:>12}'


def add_diff(diffs: List[Diff], player_name: str, level: Level, score_type: ScoreType, old: str, new: str):
    if old != new:
        diffs.append(Diff(player_name, level, score_type.value, old, new))


def records_diff(player_name: str, old: Records, new: Records) -> List[Diff]:
    diffs: List[Diff] = []
    for level in old.levels():
        old_score: Score = old.get(level)
        new_score: Score = new.get(level)
        add_diff(diffs, player_name, level, ScoreType.SPEED, old_score.speed, new_score.speed)
        add_diff(diffs, player_name, level, ScoreType.DEATH, old_score.deaths, new_score.deaths)
    return diffs


def board_diff(old: Scoreboard, new: Scoreboard) -> List[Diff]:
    diffs: List[Diff] = []
    for player_name in old.players():
        first_records = old.get(player_name)
        second_records = new.get(player_name)
        diffs += records_diff(player_name, first_records, second_records)
    return diffs


def add_diffs(new_board: Scoreboard):
    previous_times: List[List[str]] = from_csv(PREVIOUS_FILE)
    old_board: Scoreboard = Scoreboard(new_board.players(), previous_times)

    diffs: List[Diff] = board_diff(old_board, new_board)
    if len(diffs) == 0:
        print("No diffs.")
    else:
        print("Diffs:")
        for diffy in diffs:
            print("\t", diffy)

    write_diffs(diffs)


def line_to_diff(line: str) -> Diff:
    split: List[str] = line.split(",")
    return Diff(
        date=split[0],
        player_name=split[1],
        level=Level(split[2], split[3]),
        score_type=split[4],
        old=split[5],
        new=split[6]
    )


def read_diffs() -> List[Diff]:
    return [line_to_diff(diffy) for diffy in from_file(DIFFS_FILE)[1:]]


def write_diffs(new_diffs: List[Diff]) -> None:
    prev_diffs: List[str] = from_file(DIFFS_FILE)
    all_diffs: List[str] = prev_diffs + [diffy.csv_string() for diffy in new_diffs]
    to_file(DIFFS_FILE, all_diffs)