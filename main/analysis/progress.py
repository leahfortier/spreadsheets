from typing import List

from main.analysis.diffs import Diff, read_diffs
from main.data.player import Player
from main.data.progress import Progress, ProgressMap
from main.data.score import SCORE_TYPES
from main.data.scoreboard import Scoreboard
from main.util.constants import PROGRESS_FILE
from main.util.file_io import to_csv


def handle_progress(board: Scoreboard):
    progress_map = add_progress(board)
    write_progress(board, progress_map)


def add_progress(board: Scoreboard) -> ProgressMap:
    progress_map = ProgressMap()
    for player_name in board.players():
        player: Player = board.get(player_name)
        for level in player.levels():
            progress_map.add_score(player_name, level, player.get(level))

    changelog: List[Diff] = read_diffs()
    for diffy in reversed(changelog):
        progress_map.add_event(diffy)
    return progress_map


def write_progress(board: Scoreboard, progress_map: ProgressMap):
    rows: List[List[str]] = [['Date', 'Player', 'Mode', 'Chapter', 'Type', 'Value']]
    for player_name in board.players():
        player: Player = board.get(player_name)
        for level in player.levels():
            for score_type in SCORE_TYPES:
                progress: Progress = progress_map.get(player_name, level, score_type)
                for event in reversed(progress.events):
                    rows.append([
                        event.date,
                        player_name,
                        level.mode,
                        level.chapter,
                        score_type.value,
                        event.value
                    ])
    to_csv(PROGRESS_FILE, rows)
