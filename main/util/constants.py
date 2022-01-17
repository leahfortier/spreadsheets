from main.util.file_io import with_path

# Spreadsheet Link: https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>
SPREADSHEET_ID = '1Sj8JsgVGipsAsHq5V4AIrLnBf_vzHmUbSWN2WnZAiZI'
TAB_NAME = 'Scoreboard'

MODE = 'Mode'
CHAPTER = 'Chapter'
RESERVED = [MODE, CHAPTER]

DEFAULT_DATE = '01/01/22'

PREVIOUS_FILE = with_path('previous.csv')
DIFFS_FILE = with_path('changelog.txt')
PROGRESS_FILE = with_path('progress.txt')

CREDENTIALS_FILE = with_path('credentials.json')
PICKLE_FILE = with_path('token.pickle')
