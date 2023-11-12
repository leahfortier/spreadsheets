from typing import List, Optional, Dict

from main.pokehome.constants.io import FILE_PATH, ABILITIES_INFILE, ABILITIES_OUTFILE, REGIONS_OUTFILE, \
    FAMILIES_INFILE, FAMILIES_OUTFILE, GENDER_INFILE, GENDER_OUTFILE
from main.pokehome.constants.pokes import REGIONALS, TOTAL_POKEMON, NON_HOME_FORMS
from main.pokehome.constants.sheets import EMPTY_ABILITY, get_dex_sheet, GenderRatio
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv, to_file, from_file
from main.util.general import remove_suffix, has_prefix, remove_prefix


def set_abs(db_row: DbRow, abilities: List[str]):
    def ab_format(s: str):
        if s.endswith("+"):
            return s[:s.rindex("Gen ")]
        return s or EMPTY_ABILITY

    db_row.ability1 = ab_format(abilities[0])
    db_row.ability2 = ab_format(abilities[1])
    db_row.hidden = ab_format(abilities[2])


def handle_abilities(db: Database, ability_map: Dict[str, List[str]], bulba_row: List[str]):
    num = bulba_row[0]
    species = bulba_row[1]
    abilities = bulba_row[-3:]

    form_name = ""
    regional_form = ""

    if len(bulba_row) > 6:
        form_name = " ".join(bulba_row[3:-3])
        # print(form_name, bulba_row)

        for regional in REGIONALS:
            if form_name.startswith(regional):
                regional_form = regional
                prefixes = [regional + " Form", regional + " " + species]
                assert has_prefix(form_name, prefixes)
                form_name = remove_prefix(form_name, prefixes)
                break

        form_name = form_name.strip(" ()")
        form_name = remove_suffix(form_name, [" Form", " Forme", " Cloak", " Rotom", " Plumage", " Style", " Breed"])
        if form_name in ["Normal", "Standard Mode"]:
            form_name = ""
        if species == "Tauros" and regional_form == "Paldean" and form_name == "Combat":
            form_name = ""

        if has_prefix(form_name, ["Mega ", "Primal "]):
            return
        if form_name in NON_HOME_FORMS.get(species, []):
            return

    all_forms = db.species_map.get(species)
    if num not in ability_map:
        db_row = db.get(all_forms[0])
        assert db_row.is_base_form(regional_is_base=False)
        set_abs(db_row, abilities)
        ability_map[num] = abilities

        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if not form_db_row.regional_form:
                set_abs(form_db_row, abilities)
    elif regional_form and not form_name:
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form_db_row.regional_form == regional_form:
                assert form_db_row.ability1 == EMPTY_ABILITY
                set_abs(form_db_row, abilities)
    else:
        assert form_name
        db_row = None
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if regional_form and form_db_row.regional_form != regional_form:
                continue

            check_names = [form_db_row.name, form_db_row.form, form_db_row.gender_form]
            if form_name in check_names:
                db_row = form_db_row
                break

        if db_row:
            set_abs(db_row, abilities)
        elif abilities != ability_map[num]:
            print("No match for", form_name, bulba_row)


def write_abilities(db: Database):
    # Input file is copy-pasted table from Bulbapedia
    #   - Rows between generations are removed
    #   - Several form names have been edited to match
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability
    bulba_rows: List[List[str]] = from_tsv(ABILITIES_INFILE)
    ability_map: Dict[str, List[str]] = {}
    merged_row: List[str] = []

    for db_row in db.rows:
        set_abs(db_row, ["", "", ""])

    first = True
    for row in bulba_rows:
        if not first and row[0].isnumeric():
            handle_abilities(db, ability_map, merged_row)
            merged_row = []
        first = False
        merged_row.extend(row)
    handle_abilities(db, ability_map, merged_row)

    # Make sure every row has been set
    for db_row in db.rows:
        assert db_row.ability1 != EMPTY_ABILITY

    def get_abilities(row: DbRow) -> List[str]:
        return [row.ability1, row.ability2, row.hidden]

    to_tsv(ABILITIES_OUTFILE, [get_abilities(row) for row in db.rows])


def write_genders(db: Database):
    # Input file is copy-pasted table from Bulbapedia
    #   - Manually created section titles with new lines between sections
    #     - "[Can/Cannot] Breed: <GenderRatio>"
    #   - A few special Pokemon rows have been removed (Cap Pikachu etc.)
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_gender_ratio
    bulba_rows = from_tsv(GENDER_INFILE)
    in_section = False
    gender_ratio: GenderRatio = GenderRatio.GENDERLESS
    can_breed: bool = False
    for row in bulba_rows:
        if len(row) == 0:
            in_section = False
        elif in_section:
            assert len(row) == 3
            assert row[1] == row[2]
            species = row[1]
            forms = db.species_map.get(species)
            for form in forms:
                row = db.get(form)
                row.gender_ratio = gender_ratio
                row.can_breed_field = "Yes" if can_breed else "No"
        else:
            section: str = row[0]
            types = section.split(": ")
            assert len(types) == 2
            assert types[0] in ["Can Breed", "Cannot Breed"]
            can_breed = types[0] == "Can Breed"
            gender_ratio = GenderRatio(types[1])
            in_section = True

    to_tsv(GENDER_OUTFILE, [[row.can_breed_field, row.gender_ratio] for row in db.rows])


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


def write_families(db: Database):
    evolutions = from_file(FAMILIES_INFILE)

    def get_family(name: str) -> Optional[str]:
        value = None
        for evos in evolutions:
            pokes = evos.split(sep=", ")
            for poke in pokes:
                if poke == name:
                    if value:
                        print("Duplicate family for " + name)
                    value = evos
        return value

    out_rows: List[str] = []
    for row in db.rows:
        name = row.species

        family = get_family(name)
        if not family:
            family = get_family(row.name)

        if not family:
            print("No evolution found for " + name)

        out_rows.append(family or "--")

    to_file(FAMILIES_OUTFILE, out_rows)


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


def run_commands(db: Database, dex: Dex):
    write_abilities(db)
    write_genders(db)
    write_regions(db)
    write_families(db)
    write_pla_names(db)
    # compare_version_history(dex)
