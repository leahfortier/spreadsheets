from main.analysis.best import best_possible
from main.analysis.diffs import add_diffs
from main.analysis.progress import handle_progress
from main.analysis.showdown import read_showdown
from main.data.data import read_item_sheet, Data
from main.util.file_io import to_csv
from main.data.scoreboard import Scoreboard
from main.util.constants import TAB_NAME, PREVIOUS_FILE


def main():
    sheet_data: Data = read_item_sheet(TAB_NAME)
    board: Scoreboard = sheet_data.to_board()

    add_diffs(board)
    best_possible(board)
    handle_progress(board)
    read_showdown('01/14/2022 Any%', board)

    to_csv(PREVIOUS_FILE, sheet_data.rows)


main()
