from main.celeste.analysis.best import best_possible
from main.celeste.analysis.diffs import add_diffs
from main.celeste.analysis.progress import handle_progress
from main.celeste.analysis.showdown import read_showdown
from main.celeste.constants import PREVIOUS_FILE, SHOWDOWN_TABS, get_sheet_rows, BOARD_TAB
from main.celeste.data.scoreboard import Scoreboard, get_scoreboard
from main.util.data import Sheet
from main.util.file_io import to_csv


def main():
    sheet_data: Sheet = get_sheet_rows(BOARD_TAB)
    board: Scoreboard = get_scoreboard(sheet_data)

    add_diffs(board)
    best_possible(board)
    handle_progress(board)
    read_showdown(SHOWDOWN_TABS[-1], board)

    to_csv(PREVIOUS_FILE, sheet_data.rows)


main()
