import re
from datetime import date as datetime
from typing import List

from main.data.level import MODES
from main.data.score import Score
from main.util.file_io import from_csv, from_file, to_file
from main.data.records import Records
from main.data.scoreboard import Scoreboard
from main.util.constants import PREVIOUS_FILE, DIFFS_FILE


class Diff:
    def __init__(self, player_name: str, level: str, old: str, new: str, date: str = None):
        self.date: str = date or datetime.today().strftime("%m/%d/%y")
        self.player_name = player_name
        self.level = level
        self.old = old
        self.new = new
        self.type = 'Deaths' if self.new.isnumeric() else 'Speed'

        match = re.compile(level_re_grouped).match(level)
        self.mode = match.group(1)
        self.chapter = match.group(2).strip()

    def csv_string(self):
        return ','.join([self.date, self.player_name, self.mode, self.chapter, self.type, self.old, self.new])

    def __str__(self):
        return f'{self.date}' \
               f'\t{self.player_name:10}' \
               f'\t{self.level:30}' \
               f'\t{self.old:>12}' \
               f'\t{self.new:>12}'


modes_re = '|'.join([mode.value for mode in MODES])

date_re = '[0-9]{2}/[0-9]{2}/[0-9]{2}'      # Ex: 01/16/22
name_re = '[A-Z][a-z]*'                     # Ex: Melanie
section_re = '[A-Za-z0-9%\\- ]+'            # Ex: Golden Ridge, Any%
level_re = f'(?:{modes_re}) - {section_re}'     # Ex: C-Side - The Summit
level_re_grouped = f'({modes_re}) - ({section_re})'     # Ex: C-Side - The Summit
value_re = '[0-9\\-:.]+'                    # Ex: 11:48.594, 28, --
diff_format = f'({date_re})' \
              f'\\s+({name_re})' \
              f'\\s+({level_re})' \
              f'\\s+({value_re})' \
              f'\\s+({value_re})'


def matchy(diffy: str = None):
    diffy = diffy or 'A-Side - Forsaken City'
    format = level_re
    if not re.fullmatch(format, diffy):
        print("No match", diffy)
    else:
        print('Match!', diffy)


def to_diff(diffy: str) -> str:
    if not re.fullmatch(diff_format, diffy):
        print("No match", diffy)

    match = re.compile(diff_format).match(diffy)
    diff = Diff(
        date=match.group(1),
        player_name=match.group(2),
        level=match.group(3),
        old=match.group(4),
        new=match.group(5)
    )
    return diff.csv_string()


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


def add_diffs(new_board: Scoreboard):
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
    check_diffs()


def check_diffs():
    # matchy()
    new_diffs: List[str] = [to_diff(diffy) for diffy in from_file(DIFFS_FILE)]
    to_file(DIFFS_FILE, new_diffs)
    for diffy in new_diffs:
        print(diffy)




