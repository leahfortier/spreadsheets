from main.analysis.best import best_possible
from main.analysis.diffs import check_diffs
from main.data.data import read_item_sheet, Data
from main.util.file_io import to_csv
from main.data.scoreboard import Scoreboard
from main.util.constants import TAB_NAME, PREVIOUS_FILE


def main():
    sheet_data: Data = read_item_sheet(TAB_NAME)
    board: Scoreboard = Scoreboard(sheet_data.player_names, sheet_data.rows)

    check_diffs(board)
    best_possible(board)

    to_csv(PREVIOUS_FILE, sheet_data.rows)


main()
