from main.pokehome.db import Database
from main.pokehome.dex import Dex
from main.pokehome.stats import get_stats
from main.pokehome.validation import validate_dex


def main():
    db: Database = Database()
    dex: Dex = Dex(db)

    validate_dex(dex.sheet)
    db.write()
    dex.write()
    get_stats(dex)

main()