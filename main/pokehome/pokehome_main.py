from main.pokehome.commands import run_commands
from main.pokehome.db import Database
from main.pokehome.dex import Dex
from main.pokehome.stats import get_stats
from main.pokehome.validation import run_validation


def main():
    db: Database = Database()
    dex: Dex = Dex(db)

    run_commands(db, dex)
    run_validation(db, dex)

    db.write()
    dex.write()
    get_stats(dex)


main()