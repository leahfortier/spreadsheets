from main.pokehome.commands import run_commands
from main.pokehome.db import Database
from main.pokehome.dex import Dex
from main.pokehome.stats import write_stats
from main.pokehome.validation import run_validation
from pokehome.doku import Doku


def main():
    db: Database = Database()
    dex: Dex = Dex(db)
    doku: Doku = Doku(db)

    run_commands(db, dex)
    run_validation(db, dex)

    db.write()
    dex.write()
    doku.write()
    write_stats(dex, doku)


main()