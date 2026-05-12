from main.pokehome.commands import run_commands
from main.pokehome.db import Database
from main.pokehome.dex import Dex
from main.pokehome.stats import write_stats
from main.pokehome.validation import run_validation
from pokehome.doku import Doku, DokuDiffs
from pokehome.doku_masters import DokuMasters
from pokehome.go import GoDex
from pokehome.pokopia import Pokopia


def main():
    pk: Pokopia = Pokopia()
    pk.write()


main()