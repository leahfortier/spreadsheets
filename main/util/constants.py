from main.util.file_io import with_path

CREDENTIALS_FOLDER = "creds/"

CREDENTIALS_FILE = with_path(CREDENTIALS_FOLDER + 'credentials.json')
PICKLE_FILE = with_path(CREDENTIALS_FOLDER + 'token.pickle')
TOKEN_FILE = with_path(CREDENTIALS_FOLDER + 'token.json')
