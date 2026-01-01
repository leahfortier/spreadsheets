import re
from typing import List, Optional, Dict, Callable, Set, Tuple

from main.pokehome.constants.io import OUT_PATH, ABILITIES_INFILE, ABILITIES_OUTFILE, REGIONS_OUTFILE, \
    FAMILIES_INFILE, FAMILIES_OUTFILE, GENDER_INFILE, GENDER_OUTFILE, TYPES_INFILE, TYPES_OUTFILE, CATCH_RATE_INFILE, \
    CATCH_RATE_OUTFILE, IN_PATH, BABY_INFILE, FOSSIL_INFILE, CATEGORY_OUTFILE, LEGENDARY_INFILE, MYTHICAL_INFILE, \
    PARTNER_INFILE, ULTRA_INFILE, PARADOX_INFILE
from main.pokehome.constants.pokes import REGIONALS, TOTAL_POKEMON, ALL_TYPES, DIGIMON, DIGIMON_TYPES, \
    CURRENT_GENERATION
from main.pokehome.constants.sheets import EMPTY_FIELD, get_dex_sheet, GenderRatio, EvolutionType, DB_TRUE, DB_FALSE, \
    DbFields
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex
from main.util.data import Sheet, CHECKBOX_FALSE, CHECKBOX_TRUE
from main.util.file_io import to_tsv, from_tsv, to_file, from_file
from main.util.general import remove_suffix, has_prefix, remove_prefix
from main.util.warn import warn, GuardDog, message_guardian

guard = GuardDog()


class FormName:
    @message_guardian(guard)
    def __init__(self, species: str, form_name: str):
        self.species = species
        self.form_name = form_name
        self.regional = ""
        self.digimon = ""

        guard.append_message(f"{species}, {form_name}")

        if self.form_name:
            for regional in REGIONALS:
                if self.form_name.startswith(regional):
                    self.regional = regional
                    prefixes = [f'{regional} Form', f'{regional} {species}']
                    guard.prefix(self.form_name, prefixes)
                    self.form_name = remove_prefix(self.form_name, *prefixes)
                    break

            for digimon in DIGIMON:
                if self.form_name.startswith(f"{digimon} "):
                    prefixes = [f'{digimon} {species}']
                    guard.prefix(self.form_name, prefixes)
                    self.digimon = digimon + remove_prefix(self.form_name, *prefixes)
                    self.form_name = ""
                    break

            self.form_name = self.form_name.strip(" ()")
            self.form_name = remove_suffix(
                self.form_name,
                *[
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


@message_guardian(guard)
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
    guard.append_message(f'{species} {all_forms}')
    updated = []

    def update_values(db_row: DbRow):
        set_values(db_row, values)
        updated.append(db_row)

    # Base form is always first -- fill in all forms with their default values
    if num not in values_map:
        db_row = db.get(all_forms[0])
        guard.sniff(db_row.is_base_form(regional_is_base=False), "Base form must be first")
        update_values(db_row)
        values_map[num] = values
        updated.append(db_row)

        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if not form_db_row.regional_form:
                update_values(form_db_row)
    elif form.digimon:
        guard.falsy(form.regional, "No regional digimon")
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form_db_row.digimon_form == form.digimon and form_db_row.form == form.form_name:
                update_values(form_db_row)
    elif form.regional and not form.form_name:
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form_db_row.regional_form == form.regional:
                if species == "Darmanitan":
                    pass
                else:
                    guard.eq(get_first(form_db_row), EMPTY_FIELD, "First regional form should be empty")
                update_values(form_db_row)
    else:
        guard.truthy(form.form_name, "Form must exist")
        for form_id in all_forms[1:]:
            form_db_row = db.get(form_id)
            if form.regional and form_db_row.regional_form != form.regional:
                continue

            check_names = [form_db_row.name, form_db_row.form, form_db_row.gender_form]
            if form.form_name in check_names:
                update_values(form_db_row)

        guard.bark_if(not updated and values != values_map[num], f'No match for {form.form_name}')

    return updated


def set_abs(db_row: DbRow, abilities: List[str]):
    def ab_format(s: str):
        if s.endswith("+"):
            return s[:s.rindex("Gen ")]
        return s or EMPTY_FIELD

    db_row.ability1 = ab_format(abilities[0])
    db_row.ability2 = ab_format(abilities[1])
    db_row.hidden = ab_format(abilities[2])


@message_guardian(guard)
def handle_abilities(db: Database, ability_map: Dict[str, List[str]], bulba_row: List[str]):
    guard.append_message(str(bulba_row))

    num = bulba_row[0]
    species = bulba_row[1]
    abilities = bulba_row[-3:]

    form_name = ""
    if len(bulba_row) > 6:
        form_name = " ".join(bulba_row[3:-3])

    form_name = FormName(species, form_name)
    guard.append_message(str(form_name))

    updated = handle_values(
        db, species, num,
        form_name,
        ability_map, abilities,
        set_abs, lambda db_row: db_row.ability1
    )
    guard.bark_if(form_name.digimon and not updated, f"No ability found")


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
        with message_guardian(guard, db_row.name):
            guard.uneq(db_row.ability1, EMPTY_FIELD, "Empty ability")

    def get_abilities(row: DbRow) -> List[str]:
        return [row.ability1, row.ability2, row.hidden]

    to_tsv(ABILITIES_OUTFILE, [get_abilities(row) for row in db.rows])


@message_guardian(guard)
def set_types(db_row: DbRow, types: List[str]):
    guard.append_message(f"{db_row.name} {types}")

    def type_format(s: str):
        guard.truthy(s in ALL_TYPES or s == EMPTY_FIELD, f"Invalid type {s}")
        return s

    guard.truthy(types[0] != types[1] or types[0] == EMPTY_FIELD, "Same dual type")
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
        guard.uneq(db_row.type1, EMPTY_FIELD, "Empty type")

    def get_types(row: DbRow) -> List[str]:
        return [row.type1, row.type2]

    to_tsv(TYPES_OUTFILE, [get_types(row) for row in db.rows])


@message_guardian(guard)
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
    for wiki_row in bulba_rows:
        guard.append_message(str(wiki_row))
        if len(wiki_row) == 0:
            in_section = False
        elif in_section:
            guard.kill.eq(len(wiki_row), 3, "Unexpected row format")
            guard.bark.eq(wiki_row[1], wiki_row[2], "Unexpected row format")

            species = wiki_row[1]
            forms = db.species_map.get(species)
            for form in forms:
                db_row = db.get(form)
                db_row.gender_ratio = gender_ratio
                db_row.can_breed_field = DB_TRUE if can_breed else DB_FALSE
        else:
            section: str = wiki_row[0]
            types = section.split(": ")
            guard.kill.eq(len(types), 2, "Unexpected row format")
            guard.kill.inside(types[0], ["Can Breed", "Cannot Breed"])
            can_breed = types[0] == "Can Breed"
            gender_ratio = GenderRatio(types[1])
            in_section = True
        guard.pop_message(str(wiki_row))

    to_tsv(GENDER_OUTFILE, [[db_row.can_breed_field, db_row.gender_ratio] for db_row in db.rows])


@message_guardian(guard)
def get_generation(num: int) -> int:
    guard.range(num, 1, TOTAL_POKEMON)
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
            warn(f"Unknown regional form {row.regional_form} for {row.name}")
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

        if row.species in ["Dialga", "Palkia"] and row.form == "Origin":
            assert region == "Sinnoh"
            region = "Hisui"
        elif row.species == "Zygarde" and not row.is_base_form() and not row.evolution_type == EvolutionType.MEGA:
            assert region == "Kalos"
            region = "Alola"

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
    assert not (name in pre_pokes and name in post_pokes), f'{name}, {pre_pokes}, {post_pokes}'

    if name in pre_pokes:
        if row.evolution_type == EvolutionType.NONE:
            row.evolution_type = EvolutionType.FIRST
        elif row.evolution_type == EvolutionType.FINAL:
            row.evolution_type = EvolutionType.MIDDLE
        else:
            warn(f"Invalid family for {name}: {pre_pokes}, {post_pokes}")

        if len(post_pokes) > 1:
            row.has_branch_evo = DB_TRUE

    if name in post_pokes:
        if row.evolution_type == EvolutionType.NONE:
            row.evolution_type = EvolutionType.FINAL
        elif row.evolution_type == EvolutionType.FIRST:
            row.evolution_type = EvolutionType.MIDDLE
        else:
            warn(f"Invalid family for {name}: {pre_pokes}, {post_pokes}")


def handle_evolution(name: str, family: str, row: DbRow):
    row.has_branch_evo = DB_FALSE
    row.evolution_type = EvolutionType.NONE
    found = False

    if row.digimon_form.startswith("Mega") or row.digimon_form == "Primal":
        row.evolution_type = EvolutionType.MEGA
        return
    elif row.digimon_form in ["Gigantamax", "Eternamax"]:
        row.evolution_type = EvolutionType.GMAX
        return

    # Ex:
    #    ['Bulbasaur -> Ivysaur -> Venusaur']
    #    ['Wurmple -> Silcoon, Cascoon', 'Silcoon -> Beautifly', 'Cascoon -> Dustox']
    lines = family.split(" | ")
    for line in lines:
        pokes = get_family_pokes(line)
        if name in pokes:
            found = True
            stages = line.split(" -> ")
            if len(stages) == 2:
                handle_stage(name, stages[0], stages[1], row)
            elif len(stages) == 3:
                handle_stage(name, stages[0], stages[1], row)
                handle_stage(name, stages[1], stages[2], row)
            elif len(stages) != 1:
                warn(f"Unable to parse stages for {name}: {family}")
    assert found, f'{name} {family}'


def write_families(db: Database):
    evolutions = from_file(FAMILIES_INFILE)
    family_map: Dict[str, Set[str]] = {family: get_family_pokes(family) for family in evolutions}

    def get_family(form_name: str) -> Optional[str]:
        value = None
        for family, pokes in family_map.items():
            if form_name in pokes:
                if value:
                    warn("Duplicate family for " + form_name)
                value = family
        return value

    for row in db.rows:
        def get_name_and_family() -> Tuple[str, str]:
            names = [row.name, row.regional_name(), row.get_name(exclude_digimon=True)]
            for form_name in names:
                family = get_family(form_name)
                if family:
                    return form_name, family
            assert False, f"No evolution found for {names}"

        name, family = get_name_and_family()
        row.family = family or EMPTY_FIELD
        handle_evolution(name, family, row)

    def to_row(row: DbRow) -> List[str]:
        return [row.has_branch_evo, row.evolution_type, row.family]

    to_tsv(FAMILIES_OUTFILE, [to_row(row) for row in db.rows])


def write_categories(db: Database):
    babies: Set[str] = set(from_file(BABY_INFILE))
    fossils: Set[str] = set(from_file(FOSSIL_INFILE))
    partners: Set[str] = set(from_file(PARTNER_INFILE))
    legendaries: Set[str] = set(from_file(LEGENDARY_INFILE))
    mythicals: Set[str] = set(from_file(MYTHICAL_INFILE))
    paradoxicals: Set[str] = set(from_file(PARADOX_INFILE))
    ultras: Set[str] = set(from_file(ULTRA_INFILE))

    for row in db.rows:
        def get_truth(all_species: Set[str]) -> str:
            return DB_TRUE if row.species in all_species or row.name in all_species else DB_FALSE

        row.baby = get_truth(babies)
        row.fossil = get_truth(fossils)
        row.partner = get_truth(partners)
        row.legendary = get_truth(legendaries)
        row.mythical = get_truth(mythicals)
        row.paradox = get_truth(paradoxicals)
        row.ultra = get_truth(ultras)

    def to_row(row: DbRow) -> List[str]:
        return [row.baby, row.fossil, row.partner, row.legendary, row.mythical, row.paradox, row.ultra]

    to_tsv(CATEGORY_OUTFILE, [to_row(row) for row in db.rows])


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


@message_guardian(guard)
def write_regional_dex(db: Database, path_base: str):
    guard.append_message(path_base)
    in_rows = from_tsv(IN_PATH + f"{path_base}-names.in")
    out_rows = []
    update_rows = []

    dex_num = 0
    current_species = ""

    seen_ids: Set[str] = set()
    for row in in_rows:
        guard.kill.eq(len(row), 1, str(row))
        name = row[0]
        guard.append_message(name)

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

        out_dex = ""
        if species != current_species:
            dex_num += 1
            current_species = species
            out_dex = str(dex_num)

        guard.nonside(form_id, seen_ids)
        seen_ids.add(form_id)

        out_rows.append([out_dex, form_id, name, poke.image, poke.shiny_image])

        guard.pop_message(name)

    to_tsv(OUT_PATH + f"{path_base}-names.out", out_rows)


# Can use this command if needing to add several new rows in the spreadsheet at once
# Will need to be manually edited as needed for whatever is adding
# Not perfect and requires some amount of manual followup
def add_new_rows(db: Database):
    new_megas = [
        "Clefable", "Victreebel", "Starmie", "Dragonite", "Meganium", "Feraligatr", "Skarmory",
        "Froslass", "Scrafty", "Emboar", "Eelektross", "Chandelure", "Excadrill", "Scolipede",
        "Pyroar", "Barbaracle", "Dragalge", "Hawlucha", "Floette", "Malamar", "Zygarde", "Delphox",
        "Greninja", "Chesnaught", "Drampa", "Falinks",
    ]

    added = set()

    while len(added) < len(new_megas):
        for index, sheet_row in enumerate(db.sheet.rows):
            db_row = DbRow(db.sheet, sheet_row, index)
            if db_row.species in new_megas and db_row.species not in added and not db.rows[index+1].species == db_row.species:
                added.add(db_row.species)
                print(f"Adding {db_row.species}: {len(added)}")

                new_row = sheet_row.copy()

                db.sheet.update(new_row, DbFields.DIGIMON_FORM, "Mega", print_diff=(len(db_row.digimon_form) > 0))
                db.sheet.update(new_row, DbFields.FORM_ID, "-m", print_diff=(len(db_row.form_id) > 0))
                db.sheet.update(new_row, DbFields.EVO_TYPE, "Mega", print_diff=False)

                db.sheet.update(new_row, DbFields.ABILITY1, EMPTY_FIELD, print_diff=False)
                db.sheet.update(new_row, DbFields.ABILITY2, EMPTY_FIELD, print_diff=False)
                db.sheet.update(new_row, DbFields.HIDDEN_ABILITY, EMPTY_FIELD, print_diff=False)

                db.sheet.rows.insert(index+1, new_row)
                break


def compare_version_history(dex: Dex):
    previous: Sheet = get_dex_sheet()
    current: Sheet = dex.sheet

    guard.kill.len(previous.rows, current.rows)
    diffs = []

    for prev_row, current_row in zip(previous.rows, current.rows):
        guard.kill.eq(len(prev_row), 36)
        prev_row.insert(-1, CHECKBOX_FALSE)  # Quick
        prev_row.insert(-3, CHECKBOX_FALSE)  # Dusk
        guard.kill.eq(len(prev_row), 38)

        if prev_row != current_row:
            guard.kill.len(prev_row, current_row)
            rows_diffs = []
            for index, (prev_val, current_val) in enumerate(zip(prev_row, current_row)):
                if prev_val == CHECKBOX_FALSE and current_val == CHECKBOX_TRUE:
                    rows_diffs.append(f"\t{dex.sheet.schema_row[index]}++")
                elif prev_val.replace("\n", " ") != current_val.replace("\n", " "):
                    rows_diffs.append(
                        f"\t{dex.sheet.schema_row[index]}: {prev_val} -> {current_val}".replace("\n", " "))

            if len(rows_diffs) > 0:
                diffs.append(f"Diff: {current_row[0]} {current_row[3]}")
                diffs.extend(rows_diffs)

    to_file(OUT_PATH + "diffs.out", diffs)


def run_commands(db: Database):
    write_abilities(db)
    write_types(db)
    write_genders(db)
    write_regions(db)
    write_families(db)
    write_categories(db)
    write_catch_rates(db)

    write_regional_dex(db, "pla")
    write_regional_dex(db, "za")
