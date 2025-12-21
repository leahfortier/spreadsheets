from main.pokehome.commands import run_commands
from main.pokehome.db import Database
from main.pokehome.dex import Dex
from main.pokehome.stats import write_stats
from main.pokehome.validation import run_validation
from pokehome.doku import Doku
from pokehome.doku_masters import DokuMasters
from pokehome.go import GoDex


def main():
    db: Database = Database()

    dex: Dex = Dex(db)
    doku: Doku = Doku(db)
    go: GoDex = GoDex(db)
    masters: DokuMasters = DokuMasters(db)

    run_commands(db)
    run_validation(db, dex, doku)

    db.write()
    dex.write()
    doku.write()
    go.write()
    masters.write()
    write_stats(dex, doku)


main()