from typing import List

from main.celeste.constants import EMPTY_FIELD, get_sheet_rows
from main.celeste.data.level import Level, Mode, FullRun
from main.celeste.data.player import Player
from main.celeste.data.score import Score, ScoreType, SCORE_TYPES
from main.celeste.data.scoreboard import Scoreboard, get_scoreboard
from main.util.data import Sheet


def add_update(updates: List[str], player_name: str, level: Level, score_type: ScoreType, current_score: Score, best_score: Score) -> None:
    current: str = current_score.get(score_type)
    if current == EMPTY_FIELD:
        return
    best: str = best_score.get(score_type)
    current_value: int = current_score.get_value(score_type)
    best_value: int = current_value + 1 if best == EMPTY_FIELD else best_score.get_value(score_type)
    if current_value < best_value:
        updates.append(f'{player_name}: {level} - {score_type.value}: {best} -> {current}')


def read_showdown(tab_name: str, board: Scoreboard):
    sheet_data: Sheet = get_sheet_rows(tab_name)
    showdown: Scoreboard = get_scoreboard(sheet_data)

    updates: List[str] = []
    for player_name in showdown.players():
        showdown_player: Player = showdown.get(player_name)
        player: Player = board.get(player_name)
        check_split: bool = Mode.FULL_RUN.level(FullRun.ANY_PERCENT) in showdown_player.levels()
        for level in showdown_player.levels():
            showdown_score: Score = showdown_player.get(level)
            best_score: Score = player.get(level)
            for score_type in SCORE_TYPES:
                add_update(updates, player_name, level, score_type, showdown_score, best_score)
                if check_split and level.mode == Mode.A_SIDE.value:
                    split_level: Level = Level(Mode.ANY_SPLIT.value, level.chapter)
                    best_split: Score = player.get(split_level)
                    add_update(updates, player_name, split_level, score_type, showdown_score, best_split)

    if len(updates) == 0:
        print(f'No updates for {tab_name}.')
    else:
        print(f'Updates from {tab_name}!!!!!:')
        for update in updates:
            print('\t', update)
