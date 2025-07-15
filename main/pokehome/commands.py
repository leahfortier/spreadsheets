from typing import List, Optional, Dict, Callable, Set
import re

from main.pokehome.constants.io import OUT_PATH, ABILITIES_INFILE, ABILITIES_OUTFILE, REGIONS_OUTFILE, \
    FAMILIES_INFILE, FAMILIES_OUTFILE, GENDER_INFILE, GENDER_OUTFILE, TYPES_INFILE, TYPES_OUTFILE, CATCH_RATE_INFILE, \
    CATCH_RATE_OUTFILE, IN_PATH
from main.pokehome.constants.pokes import REGIONALS, TOTAL_POKEMON, ALL_TYPES, DIGIMON, DIGIMON_TYPES, \
    CURRENT_GENERATION
from main.pokehome.constants.sheets import EMPTY_FIELD, get_dex_sheet, GenderRatio, EvolutionType
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex
from main.util.data import Sheet
from main.util.file_io import to_tsv, from_tsv, to_file, from_file
from main.util.general import remove_suffix, has_prefix, remove_prefix


class FormName:
    def __init__(self, species: str, form_name: str):
        self.species = species
        self.form_name = form_name
        self.regional = ""
        self.digimon = ""

        if self.form_name:
            for regional in REGIONALS:
                if self.form_name.startswith(regional):
                    self.regional = regional
                    prefixes = [regional + " Form", regional + " " + species]
                    assert has_prefix(self.form_name, prefixes)
                    self.form_name = remove_prefix(self.form_name, prefixes)
                    break

            for digimon in DIGIMON:
                if self.form_name.startswith(f"{digimon} "):
                    prefixes = [digimon + " " + species]
                    assert has_prefix(self.form_name, prefixes)
                    self.digimon = digimon + remove_prefix(self.form_name, prefixes)
                    self.form_name = ""
                    break

            self.form_name = self.form_name.strip(" ()")
            self.form_name = remove_suffix(
                self.form_name,
                [
                    f" {species}",
                    " Form", " Forme",
                    " Cloak", " Rotom", " Plumage", " Style", " Breed",
                ]
            )
            if self.form_name in ["Normal", "Standard Mode"]:
                self.form_name = ""
            if species == "Tauros" and self.regional == "Paldean" and self.form_name == "Combat":
                self.form_name = ""
            if species == "Oricorio":
                self.form_name += " Style"

    def __repr__(self):
        return [self.species, self.form_name, self.regional, self.digimon].__repr__()

def handle_values(
        db: Database,
        species: str,
        num: str,
        form: FormName,
        values_map: Dict[str, List[str]],
        values: List[str],
        set_values: Callable[[DbRow, List[str]], None],
        get_first: Callable[[DbRow], str]
) -> List[DbRow]:
    all_forms = db.species_map.get(species)
    updated = []

    def update_values(db_row: DbRow):
        set_values(db_row, values)
        updated.append(db_row)

    # Base form is always first -- fill in all forms with their default values
    if num not in values_map:
        db_row = db.get(all_forms[0])
        assert db_row.is_base_form(regional_is_base=False)
        update_values(db_row)
        values_map[num] = values
        updated.append(db_row)

        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if not form_db_row.regional_form:
                update_values(form_db_row)
    elif form.digimon:
        assert not form.regional
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form_db_row.digimon_form == form.digimon and form_db_row.form == form.form_name:
                update_values(form_db_row)
    elif form.regional and not form.form_name:
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form_db_row.regional_form == form.regional:
                assert get_first(form_db_row) == EMPTY_FIELD or species == "Darmanitan"
                update_values(form_db_row)
    else:
        assert form.form_name
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form.regional and form_db_row.regional_form != form.regional:
                continue

            check_names = [form_db_row.name, form_db_row.form, form_db_row.gender_form]
            if form.form_name in check_names:
                update_values(form_db_row)

        if not updated and values != values_map[num]:
            print("No match for", species, form.form_name)

    return updated


def set_abs(db_row: DbRow, abilities: List[str]):
    def ab_format(s: str):
        if s.endswith("+"):
            return s[:s.rindex("Gen ")]
        return s or EMPTY_FIELD

    db_row.ability1 = ab_format(abilities[0])
    db_row.ability2 = ab_format(abilities[1])
    db_row.hidden = ab_format(abilities[2])


def handle_abilities(db: Database, ability_map: Dict[str, List[str]], bulba_row: List[str]):
    num = bulba_row[0]
    species = bulba_row[1]
    abilities = bulba_row[-3:]

    form_name = ""
    if len(bulba_row) > 6:
        form_name = " ".join(bulba_row[3:-3])

    form_name = FormName(species, form_name)
    updated = handle_values(
        db, species, num,
        form_name,
        ability_map, abilities,
        set_abs, lambda db_row: db_row.ability1
    )
    if form_name.digimon and not updated:
        print(f"Ability not found for {form_name.digimon} {species}")


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
        assert db_row.ability1 != EMPTY_FIELD

    def get_abilities(row: DbRow) -> List[str]:
        return [row.ability1, row.ability2, row.hidden]

    to_tsv(ABILITIES_OUTFILE, [get_abilities(row) for row in db.rows])


def set_types(db_row: DbRow, types: List[str]):
    def type_format(s: str):
        assert s in ALL_TYPES or s == EMPTY_FIELD
        return s

    assert types[0] != types[1] or types[0] == EMPTY_FIELD
    db_row.type1 = type_format(types[0])
    db_row.type2 = type_format(types[1])


def handle_types(db: Database, types_map: Dict[str, List[str]], num: str, bulba_row: List[str]):
    species = bulba_row[0]

    if bulba_row[-2] not in ALL_TYPES:
        bulba_row.append(EMPTY_FIELD)
    types = bulba_row[-2:]

    form_name = ""
    if bulba_row[2] not in ALL_TYPES:
        form_name = bulba_row[2]

    form_name = FormName(species, form_name)
    updated = handle_values(
        db, species, num,
        form_name,
        types_map, types,
        set_types, lambda db_row: db_row.type1
    )
    for updated_row in updated:
        if updated_row.name in DIGIMON_TYPES:
            set_types(updated_row, DIGIMON_TYPES[updated_row.name])


def write_types(db: Database):
    # Input file is copy-pasted table from Bulbapedia
    #   - Rows between generations are removed
    #   - Several form names have been edited to match
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number
    bulba_rows: List[List[str]] = from_tsv(TYPES_INFILE)
    types_map: Dict[str, List[str]] = {}
    merged_row: List[str] = []

    for db_row in db.rows:
        set_types(db_row, [EMPTY_FIELD, EMPTY_FIELD])

    odd = True
    num = 1
    for row in bulba_rows:
        if row[0].strip("#").isnumeric():
            num = row[0].strip("#")
            row = row[1:]
        merged_row.extend(row)
        if not odd:
            handle_types(db, types_map, num, merged_row)
            merged_row = []
        odd = not odd

    # Make sure every row has been set
    for db_row in db.rows:
        assert db_row.type1 != EMPTY_FIELD

    def get_types(row: DbRow) -> List[str]:
        return [row.type1, row.type2]

    to_tsv(TYPES_OUTFILE, [get_types(row) for row in db.rows])


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


def get_generation(num: int) -> int:
    assert 1 <= num <= TOTAL_POKEMON
    if num <= 151:
        return 1
    elif num <= 251:
        return 2
    elif num <= 386:
        return 3
    elif num <= 493:
        return 4
    elif num <= 649:
        return 5
    elif num <= 721:
        return 6
    elif num <= 809:
        return 7
    elif num <= 905:
        # Includes Galar and Hisui
        return 8
    else:
        return CURRENT_GENERATION


def write_regions(db: Database):
    regions = []
    for row in db.rows:
        num = int(row.dex)
        gen = get_generation(num)
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
        elif row.form == "Bloodmoon":
            region = "Paldea"
        elif gen == 1:
            region = "Kanto"
        elif gen == 2:
            region = "Johto"
        elif gen == 3:
            region = "Hoenn"
        elif gen == 4:
            region = "Sinnoh"
        elif gen == 5:
            region = "Unova"
        elif gen == 6:
            region = "Kalos"
        elif gen == 7:
            region = "Alola"
        elif gen == 8:
            if num <= 898:
                region = "Galar"
            else:
                region = "Hisui"
        else:
            region = "Paldea"

        assert 1 <= gen <= CURRENT_GENERATION
        assert region
        regions.append([str(gen), region])

    to_tsv(REGIONS_OUTFILE, regions)


# Ex:
#   Input: Wurmple -> Silcoon, Cascoon | Silcoon -> Beautifly | Cascoon -> Dustox
#   Output: {"Wurmple", "Silcoon", "Cascoon", "Beautifly", "Dustox"}
def get_family_pokes(family: str) -> Set[str]:
    return set(re.split(r' -> |, | \| ', family))


def handle_stage(name: str, pre_evs: str, post_evs: str, row: DbRow):
    pre_pokes = get_family_pokes(pre_evs)
    post_pokes = get_family_pokes(post_evs)
    assert not (name in pre_pokes and name in post_pokes)

    if name in pre_pokes:
        if row.evolution_type == EvolutionType.NONE:
            row.evolution_type = EvolutionType.FIRST
        elif row.evolution_type == EvolutionType.FINAL:
            row.evolution_type = EvolutionType.MIDDLE
        else:
            print(f"Invalid family for {name}: {pre_pokes}, {post_pokes}")

        if len(post_pokes) > 1:
            row.has_branch_evo = "Yes"

    if name in post_pokes:
        if row.evolution_type == EvolutionType.NONE:
            row.evolution_type = EvolutionType.FINAL
        elif row.evolution_type == EvolutionType.FIRST:
            row.evolution_type = EvolutionType.MIDDLE
        else:
            print(f"Invalid family for {name}: {pre_pokes}, {post_pokes}")


def handle_evolution(name: str, family: str, row: DbRow):
    row.has_branch_evo = "No"
    row.evolution_type = EvolutionType.NONE

    # Ex:
    #    ['Bulbasaur -> Ivysaur -> Venusaur']
    #    ['Wurmple -> Silcoon, Cascoon', 'Silcoon -> Beautifly', 'Cascoon -> Dustox']
    lines = family.split(" | ")
    for line in lines:
        pokes = get_family_pokes(line)
        if name in pokes:
            stages = line.split(" -> ")
            if len(stages) == 2:
                handle_stage(name, stages[0], stages[1], row)
            elif len(stages) == 3:
                handle_stage(name, stages[0], stages[1], row)
                handle_stage(name, stages[1], stages[2], row)
            elif len(stages) != 1:
                print(f"Unable to parse stages for {name}: {family}")


def write_families(db: Database):
    evolutions = from_file(FAMILIES_INFILE)
    family_map: Dict[str, Set[str]] = {family: get_family_pokes(family) for family in evolutions}

    def get_family(name: str) -> Optional[str]:
        value = None
        for family, pokes in family_map.items():
            if name in pokes:
                if value:
                    print("Duplicate family for " + name)
                value = family
        return value

    for row in db.rows:
        name = row.regional_name()

        family = get_family(name)
        if not family:
            family = get_family(row.name)
        if not family:
            print("No evolution found for " + name)

        row.family = family or EMPTY_FIELD
        handle_evolution(name, family, row)

    def to_row(row: DbRow) -> List[str]:
        return [row.has_branch_evo, row.evolution_type, row.family]

    to_tsv(FAMILIES_OUTFILE, [to_row(row) for row in db.rows])


def write_catch_rates(db: Database):
    # Input file is copy-pasted table from Bulbapedia
    #   - https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_catch_rate
    bulba_rows: List[List[str]] = from_tsv(CATCH_RATE_INFILE)

    for db_row in db.rows:
        db_row.catch_rate = EMPTY_FIELD

    for row in bulba_rows:
        assert len(row) == 4
        assert row[0].isnumeric()
        assert row[1] == row[2]

        species = row[1]
        catch_rate = row[3].rstrip("*")

        all_forms = db.species_map.get(species)
        for form_id in all_forms:
            form_db_row = db.get(form_id)
            form_db_row.catch_rate = catch_rate

    # Make sure every row has been set
    for db_row in db.rows:
        assert db_row.catch_rate != EMPTY_FIELD

    to_tsv(CATCH_RATE_OUTFILE, [[row.catch_rate] for row in db.rows])


def write_pla_names(db: Database):
    pla_rows = from_tsv(IN_PATH + "pla-names.in")
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

    to_tsv(OUT_PATH + "pla-names.out", out_rows)


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

    to_file(OUT_PATH + "diffs.out", diffs)


def run_commands(db: Database, dex: Dex):
    write_abilities(db)
    write_types(db)
    write_genders(db)
    write_regions(db)
    write_families(db)
    write_catch_rates(db)
    write_pla_names(db)
    # compare_version_history(dex)
