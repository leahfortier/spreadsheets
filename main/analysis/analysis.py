from main.analysis.best import best_possible
from main.analysis.diffs import add_diffs
from main.analysis.progress import handle_progress
from main.analysis.showdown import read_showdown
from main.data.data import read_item_sheet, Data
from main.util.file_io import to_csv
from main.data.scoreboard import Scoreboard
from main.util.constants import BOARD_TAB, PREVIOUS_FILE, SHOWDOWN_TABS


def main():
    sheet_data: Data = read_item_sheet(BOARD_TAB)
    board: Scoreboard = sheet_data.to_board()

    add_diffs(board)
    best_possible(board)
    handle_progress(board)
    read_showdown(SHOWDOWN_TABS[-1], board)

    to_csv(PREVIOUS_FILE, sheet_data.rows)


main()
