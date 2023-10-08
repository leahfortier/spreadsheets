from typing import List

from main.pokehome.constants.io import FILE_PATH, ABILITIES_INFILE, ABILITIES_OUTFILE, REGIONS_OUTFILE, \
    EVOLUTIONS_INFILE, EVOLUTIONS_OUTFILE
from main.pokehome.constants.pokes import REGIONALS, TOTAL_POKEMON
from main.pokehome.constants.sheets import EMPTY_ABILITY, get_dex_sheet
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex, DexRow
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv, to_file, from_file


def write_abilities(db: Database):
    # Input file is copy-pasted table from Bulbapedia
    #   - Rows between generations are removed
    #   - Several form names have been edited to match
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability
    bulba_rows = from_tsv(ABILITIES_INFILE)
    for index in range(0, len(bulba_rows), 2):
        first = bulba_rows[index]
        second = bulba_rows[index + 1]
        species = first[1]
        form_name = ""
        assert len(second) in [3, 4]
        if len(second) == 4:
            form_name = second[0]
            if form_name.startswith("Mega"):
                continue
            if form_name in ["Normal"]:
                form_name = ""

        def set_abs(row: DbRow):
            def ab_format(s: str):
                return (s or EMPTY_ABILITY).rstrip("*")

            row.ability1 = ab_format(second[-3])
            row.ability2 = ab_format(second[-2])
            row.hidden = ab_format(second[-1])

        forms = db.get_forms([species], regional_is_alt=True)
        for form in forms:
            row = db.get(form)
            if form_name:
                if form_name in [row.name, row.form, row.gender_form]:
                    set_abs(row)
            else:
                set_abs(row)

    def get_abilities(row: DbRow) -> List[str]:
        return [row.ability1, row.ability2, row.hidden]

    to_tsv(ABILITIES_OUTFILE, [get_abilities(row) for row in db.rows])


def write_regions(db: Database):
    regions = []
    for row in db.rows:
        num = int(row.dex)
        region = ""
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
        elif num <= TOTAL_POKEMON:
            region = "Paldea"
        else:
            print(f"Invalid dex num {num} for {row.name}")

        assert region
        regions.append([region])

    to_tsv(REGIONS_OUTFILE, [row for row in regions])


def write_evolutions(db: Database):
    evolutions = from_tsv(EVOLUTIONS_INFILE)
    out_rows = []
    for row in db.rows:
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

    to_tsv(EVOLUTIONS_OUTFILE, out_rows)


def write_pla_names(db: Database):
    pla_rows = from_tsv(FILE_PATH + "pla-names.in")
    out_rows = []
    for row in pla_rows:
        assert len(row) == 1
        name = row[0]

        species = name.rstrip("♂").rstrip("♀").strip()
        for region in REGIONALS:
            if species.startswith(region):
                species = species[len(region):].strip()

        if species not in db.species_map:
            species = species.split()[0].strip()

        forms = db.species_map[species]
        form_id = None
        if name == species:
            form_id = db.species_map.get(species)[0]
        else:
            for form in forms:
                poke = db.get(form)
                if poke.name == name:
                    form_id = form
                    break
                if name.rstrip("♂").strip() == poke.name and poke.gender_form == "Male":
                    form_id = form
                    break
                if name.rstrip("♀").strip() == poke.name and poke.gender_form == "Female":
                    form_id = form
                    break
        assert form_id is not None
        poke = db.get(form_id)

        out_rows.append([form_id, name, poke.image, poke.shiny_image])

    to_tsv(FILE_PATH + "pla-names.out", out_rows)


def compare_version_history(dex: Dex):
    previous: Sheet = get_dex_sheet()
    current: Sheet = dex.sheet

    assert len(previous.rows) == len(current.rows)
    diffs = []

    for prev_row, current_row in zip(previous.rows, current.rows):
        assert len(prev_row) == 36
        prev_row.insert(-1, 'FALSE') # Quick
        prev_row.insert(-3, 'FALSE') # Dusk
        assert len(prev_row) == 38

        if prev_row != current_row:
            assert len(prev_row) == len(current_row)
            rows_diffs = []
            for index, (prev_val, current_val) in enumerate(zip(prev_row, current_row)):
                if prev_val == "FALSE" and current_val == "TRUE":
                    rows_diffs.append(f"\t{dex.sheet.schema_row[index]}++")
                elif prev_val.replace("\n", " ") != current_val.replace("\n", " "):
                    rows_diffs.append(f"\t{dex.sheet.schema_row[index]}: {prev_val} -> {current_val}".replace("\n", " "))

            if len(rows_diffs) > 0:
                diffs.append(f"Diff: {current_row[0]} {current_row[3]}")
                diffs.extend(rows_diffs)

    to_file(FILE_PATH + "diffs.out", diffs)


def genshin_achievements_add_version_column():
    wiki = from_tsv(FILE_PATH + "achievements.in")
    version_map = {}
    for row in wiki:
        print(row)
        assert len(row) in [6, 7]
        name = row[0]
        version = row[-2]
        assert version_map.get(name, version) == version
        version_map[name] = version

    sheet = from_tsv(FILE_PATH + "GENSHIN IMPACT - Achievements.tsv")
    name_index = 9

    out = []
    for row in sheet:
        name = row[name_index]
        version = version_map.get(name, "")
        print(name, version)
        out.append([version, name])

    to_tsv(FILE_PATH + "versions-out.tsv", out)


def gensin_recipes():
    recipes = from_tsv(FILE_PATH + "recipes.in")
    character_to_recipe = {}

    for row in recipes:
        assert len(row) == 2
        recipe = row[0]
        character = row[1]
        if character:
            character_to_recipe[character] = recipe

    out = []
    characters = from_file(FILE_PATH + "characters.in")
    assert len(characters) == len(character_to_recipe)
    for character in characters:
        if character in ["Raiden Shogun", "Traveler"]:
            recipe = "None"
        else:
            recipe = character_to_recipe[character]
        out.append(recipe)

    to_file(FILE_PATH + "recipes.out", out)


def run_commands(db: Database, dex: Dex):
    write_abilities(db)
    write_regions(db)
    write_evolutions(db)
    write_pla_names(db)
    # compare_version_history(dex)
    # genshin_achievements_add_version_column()
    # gensin_recipes()
