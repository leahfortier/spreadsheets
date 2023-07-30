from main.celeste.analysis.best import best_possible
from main.celeste.analysis.diffs import add_diffs
from main.celeste.analysis.progress import handle_progress
from main.celeste.analysis.showdown import read_showdown
from main.celeste.constants import PREVIOUS_FILE, SHOWDOWN_TABS, get_sheet_rows, BOARD_TAB
from main.celeste.data.data import Data
from main.celeste.data.scoreboard import Scoreboard
from main.util.file_io import to_csv


def main():
    sheet_data: Data = Data(get_sheet_rows(BOARD_TAB))
    board: Scoreboard = sheet_data.to_board()

    add_diffs(board)
    best_possible(board)
    handle_progress(board)
    read_showdown(SHOWDOWN_TABS[-1], board)

    to_csv(PREVIOUS_FILE, sheet_data.rows)


main()
