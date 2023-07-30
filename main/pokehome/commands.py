from typing import List

from main.pokehome.constants.io import FILE_PATH, EVOLUTIONS_INFILE
from main.pokehome.constants.sheets import EMPTY_ABILITY
from main.pokehome.db import read_db, DBRow
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv, from_tsv


def write_abilities():
    # Input file is copy-pasted table from Bulbapedia
    #   - Rows between generations are removed
    #   - Several form names have been edited to match
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability
    rows = from_tsv(FILE_PATH + "abilities-in.tsv")
    dex = Dex()
    for index in range(0, len(rows), 2):
        first = rows[index]
        second = rows[index + 1]
        species = first[1]
        form_name = ""
        if len(second) == 4:
            form_name = second[0]
            if form_name.startswith("Mega"):
                continue
            if form_name in ["Normal"]:
                form_name = ""

        def ab(s: str):
            return (s or EMPTY_ABILITY).rstrip("*")

        ability1 = ab(second[-3])
        ability2 = ab(second[-2])
        hidden = ab(second[-1])
        forms = dex.name_db[species]

        def set_abs(row):
            row.ability1 = ability1
            row.ability2 = ability2
            row.hidden = hidden
            # print(row.name, ability1, ability2, hidden)

        for form in forms:
            row = dex.db.get(form)
            if form_name:
                if form_name in [row.name, row.form, row.gender_form]:
                    set_abs(row)
            else:
                set_abs(row)

    to_tsv(FILE_PATH + "abilities-out.tsv", [[row.ability1, row.ability2, row.hidden] for row in dex.db_rows])


def write_regions():
    rows: List[DBRow] = read_db()
    regions = []
    for row in rows:
        num = int(row.dex)
        region = "TODO"
        if row.regional_form == "Paldean":
            region = "Paldea"
        elif row.regional_form == "Hisuian":
            region = "Hisui"
        elif row.regional_form == "Galarian":
            region = "Galar"
        elif row.regional_form == "Alolan":
            region = "Alola"
        elif row.regional_form:
            print(f"Unknown regional form {row.regional_form} for {row.name}")
        elif num < 1:
            print(f"Invalid dex num {num} for {row.name}")
        elif num <= 151:
            region = "Kanto"
        elif num <= 251:
            region = "Johto"
        elif num <= 386:
            region = "Hoenn"
        elif num <= 493:
            region = "Sinnoh"
        elif num <= 649:
            region = "Unova"
        elif num <= 721:
            region = "Kalos"
        elif num <= 809:
            region = "Alola"
        elif num <= 898:
            region = "Galar"
        elif num <= 905:
            region = "Hisui"
        elif num <= 1010:
            region = "Paldea"
        else:
            print(f"Invalid dex num {num} for {row.name}")

        regions.append([region])

    to_tsv(FILE_PATH + "regions-out.tsv", [row for row in regions])


def write_evolutions():
    evolutions = from_tsv(EVOLUTIONS_INFILE)
    rows: List[DBRow] = read_db()
    out_rows = []
    for row in rows:
        name = row.species
        if row.regional_form:
            name = row.regional_form + " " + name

        value = None
        for evos in evolutions:
            assert len(evos) == 1
            pokes = evos[0].split(sep=", ")
            for poke in pokes:
                if poke == name:
                    if value:
                        print("Duplicate family for " + name)
                    value = evos

        if not value:
            print("No evolution found for " + name)

        out_rows.append(value or "--")

    to_tsv(FILE_PATH + "evolutions-out.tsv", out_rows)

# write_abilities()
# write_regions()
write_evolutions()