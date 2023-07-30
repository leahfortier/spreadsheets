from typing import List

from main.constants.sheet_id import CELESTE_ID
from main.util.sheets import get_sheet_data

SPREADSHEET_ID = CELESTE_ID
BOARD_TAB = 'Scoreboard'
SHOWDOWN_TABS = [
    '08/12/2018 Any%',
    '01/31/2019 Any% (1)',
    '01/31/2019 Any% (2)',
    '02/02/2019 Any%',
    '02/03/2019 Any%',
    '02/05/2019 Any%',
    '02/06/2019 Any%',
    '02/08/2019 Any%',
    '02/09/2019 Any%',
    '02/15/2019 Any%',
    '08/31/2019 Any%',
    '09/04/2019 Any%',
    '09/07/2019 100%-',
    '09/06/2020 Any%',
    '09/09/2020 100%',
    '09/11/2020 Any%',
    '09/11/2020 Invisible Any%',
    '09/18/2020 Any%',
    '09/18/2020 100%',
    '01/01/2022 100%',
    '01/02/2022 Any% (1)',
    '01/02/2022 Any% (2)',
    '01/12/2022 Any%',
    '01/14/2022 Any%',
    '01/19/2022 Any%',
    '01/21/2022 Any% (1)',
    '01/21/2022 Any% (2)',
    '01/24/2022 Any%',
]

MODE = 'Mode'
CHAPTER = 'Chapter'
RESERVED = [MODE, CHAPTER]

DEFAULT_DATE = '01/01/2022'
EMPTY_FIELD = '--'

OUT_FOLDER = "out/"

PREVIOUS_FILE = OUT_FOLDER + 'previous.csv'
DIFFS_FILE = OUT_FOLDER + 'changelog.csv'
PROGRESS_FILE = OUT_FOLDER + 'progress.csv'


def get_sheet_rows(tab_name: str) -> List[List[str]]:
    return get_sheet_data(SPREADSHEET_ID, tab_name)