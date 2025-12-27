from typing import Dict, List, Set

from main.pokehome.constants.io import ABILITIES_OUTFILE, REGIONS_OUTFILE, FAMILIES_OUTFILE, GENDER_OUTFILE, \
    BALLS_OUTFILE, TYPES_OUTFILE, CATEGORY_OUTFILE
from main.pokehome.constants.pokes import REGIONS, INCLUDE_UNBREEDABLE_POKEBALLS, BALL_NOTES
from main.pokehome.constants.sheets import DexFields, EMPTY_FIELD, HiddenAbilityProgress, SAME_ID_DIFFERENT_FIELDS, \
    DbFields, EvolutionType
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex
from main.util.data import Sheet, CHECKBOX_TRUE
from main.util.file_io import from_tsv, to_file
from pokehome.doku import Doku, DokuDiffs, DokuDiff
from util.general import all_unique, to_str
from util.warn import GuardDog, message_guardian

guard = GuardDog()


@message_guardian(guard)
def validate_dex(db: Database, sheet: Sheet):
    id_map: Dict[str, int] = {}
    hidden_families: Dict[str, bool] = {}
    ball_families: Dict[str, Set[str]] = {}
    ball_map: Dict[str, List[str]] = {}

    main_fields = [to_str(field) for field in DexFields]
    ball_fields = [field for field in sheet.schema_row if field not in main_fields]

    for index, row in enumerate(sheet.rows):
        def get(field: DexFields) -> str:
            return sheet.get(row, field.value)

        def is_caught(checkbox_field: str) -> bool:
            return sheet.get(row, checkbox_field) == CHECKBOX_TRUE

        name = get(DexFields.NAME)
        row_id = get(DexFields.ID)
        db_row = db.get(row_id)

        caught = is_caught(DexFields.CAUGHT_PROGRESS.value)
        family = db_row.family
        nickname = get(DexFields.NICKNAME)
        trainer = get(DexFields.TRAINER)
        hidden_ability = get(DexFields.HIDDEN_ABILITY)
        hidden_progress = get(DexFields.HIDDEN_PROGRESS)

        guard.append_message(f'{name} {row_id}')

        # Uncaught Pokemon should not have a nickname or OT
        guard.info_if(nickname and not caught and not nickname.startswith("TODO"), f"Uncaught with nickname: {nickname}")
        guard.info_if(trainer and not caught, f"Uncaught with trainer: {trainer}")

        # All caught Pokemon should include their OT
        guard.info_if(caught and not trainer, f"Caught without trainer")

        # Validate region
        region = get(DexFields.REGION)
        guard.inside(region, REGIONS)

        # Hidden ability matches family or N/A
        with message_guardian(guard, f'{hidden_ability}, {hidden_progress}'):
            guard.eq(db_row.hidden, hidden_ability)
            guard.inside(hidden_progress, [e for e in HiddenAbilityProgress])
            if hidden_ability == EMPTY_FIELD or name == "Pangoro":
                guard.eq(hidden_progress, HiddenAbilityProgress.NO_HIDDEN_ABILITY)
            else:
                has_hidden = hidden_progress != HiddenAbilityProgress.UNOBTAINED
                guard.eq(
                    hidden_families.get(db_row.family, has_hidden), has_hidden,
                    "Hidden progress does not match family"
                )
                hidden_families[db_row.family] = has_hidden

        # Duplicate rows (in live dex and forms) should have matching values
        if row_id in id_map:
            base_row = sheet.rows[id_map[row_id]]
            for field in sheet.schema_row:
                if field in SAME_ID_DIFFERENT_FIELDS:
                    continue
                form_value = sheet.get(row, field)
                base_value = sheet.get(base_row, field)
                if field == DexFields.BOX:
                    guard.uneq(form_value, base_value, "Non-base in Box")
                else:
                    guard.eq(form_value, base_value, f'Mismatched field {field}')
        else:
            id_map[row_id] = index

            for ball in ball_fields:
                if is_caught(ball):
                    ball_map.setdefault(ball, [])
                    ball_map.get(ball).append(name)

                    # Assert only one family member per ball
                    ball_families.setdefault(family, set())
                    if name == "Scizor" and ball == "Park":
                        guard.inside(ball, ball_families.get(family))
                    else:
                        guard.nonside(ball, ball_families.get(family), f'Duplicate ball for {family}')
                    ball_families[family].add(ball)

                    # Only collecting balls for Pokemon that can pass them down
                    guard.sniff(db_row.can_breed() or db_row.species in INCLUDE_UNBREEDABLE_POKEBALLS, f"Unbreedable with {ball}")

        guard.pop_message(f'{name} {row_id}')

    for ball in BALL_NOTES.keys():
        guard.inside(ball, ball_map)

    out: List[str] = []
    for ball, names in ball_map.items():
        out.append(f"{ball}: {len(names)}{BALL_NOTES.get(ball, '')}")
        for name in names:
            out.append("\t" + name)
        out.append("")
    to_file(BALLS_OUTFILE, out)


@message_guardian(guard)
def validate_db(db: Database):
    fossil_families: Dict[str, bool] = {}
    for row in db.rows:
        guard.append_message(row.name)

        # Baby Pokemon must be first in evolution
        if row.is_baby():
            guard.eq(row.evolution_type, EvolutionType.FIRST, "Baby")

        # Fossil status must be consistent for all family members
        fossil = row.is_fossil()
        guard.eq(fossil, fossil_families.get(row.family, fossil), f"Fossil mismatch: {row.family}")
        fossil_families[row.family] = fossil


@message_guardian(guard)
def validate_command_out(db: Database):
    db_rows: List[DbRow] = db.rows
    sheet_rows: List[List[str]] = db.sheet.rows
    ability_rows: List[List[str]] = from_tsv(ABILITIES_OUTFILE)
    type_rows: List[List[str]] = from_tsv(TYPES_OUTFILE)
    region_rows: List[List[str]] = from_tsv(REGIONS_OUTFILE)
    evolution_rows: List[List[str]] = from_tsv(FAMILIES_OUTFILE)
    gender_rows: List[List[str]] = from_tsv(GENDER_OUTFILE)
    category_rows: List[List[str]] = from_tsv(CATEGORY_OUTFILE)

    # Rows must correspond to each other
    guard.len(ability_rows, db_rows, "Abilities")
    guard.len(type_rows, db_rows, "Types")
    guard.len(region_rows, db_rows, "Regions")
    guard.len(evolution_rows, db_rows, "Evolutions")
    guard.len(gender_rows, db_rows, "Genders")
    guard.len(category_rows, db_rows, "Categories")

    guard.len(sheet_rows, db_rows, "Sheet")

    for index, row in enumerate(db_rows):
        sheet_row = sheet_rows[index]
        guard.append_message(row.name)

        # If this fails you need to either:
        #  - Update the respective DB columns with the output file
        #  - Update the input file with new data to match
        guard.eq(ability_rows[index], [row.ability1, row.ability2, row.hidden], "Abilities")
        guard.eq(type_rows[index], [row.type1, row.type2], "Types")
        guard.eq(region_rows[index], [row.generation, row.region], "Regions")
        guard.eq(evolution_rows[index], [row.has_branch_evo, row.evolution_type, row.family], "Evolutions")
        guard.eq(gender_rows[index], [row.can_breed_field, row.gender_ratio], "Genders")
        guard.eq(category_rows[index], [row.baby, row.fossil, row.partner, row.legendary, row.mythical, row.paradox, row.ultra], "Categories")

        guard.uneq(row.ability1, EMPTY_FIELD, "Empty primary ability")
        guard.uneq(row.type1, EMPTY_FIELD, "Empty primary type")
        guard.sniff(all_unique(ability_rows[index], exceptions=[EMPTY_FIELD]), f'Non-unique abilities: {ability_rows[index]}')
        guard.sniff(all_unique(type_rows[index]), f'Non-unique types: {type_rows[index]}')
        guard.inside(row.region, REGIONS)

        def print_mismatch(label: str, sheet_fields: List[DbFields], row_values: List[str]):
            sheet_values = [db.sheet.get(sheet_row, field) for field in sheet_fields]
            guard.eq(sheet_values, row_values, f'{label} mismatch')

        print_mismatch("Ability", [DbFields.ABILITY1, DbFields.ABILITY2, DbFields.HIDDEN_ABILITY], ability_rows[index])
        print_mismatch("Type", [DbFields.TYPE1, DbFields.TYPE2], type_rows[index])
        print_mismatch("Region", [DbFields.GENERATION, DbFields.OG_REGION], region_rows[index])
        print_mismatch("Family", [DbFields.HAS_BRANCH, DbFields.EVO_TYPE, DbFields.FAMILY_EVOS], evolution_rows[index])
        print_mismatch("Gender", [DbFields.CAN_BREED, DbFields.GENDER_RATIO], gender_rows[index])
        print_mismatch("Category", [DbFields.IS_BABY, DbFields.IS_FOSSIL, DbFields.IS_PARTNER, DbFields.IS_LEGENDARY, DbFields.IS_MYTHICAL, DbFields.IS_PARADOX, DbFields.IS_ULTRA_BEAST], category_rows[index])

        guard.pop_message(row.name)


@message_guardian(guard)
def validate_doku(doku: Doku):
    # Accidentally added a bunch of extra rows once by trying to update doku fields from db
    # You will need to manually delete the extra rows at the bottom of the file since correctly
    #   pasting doku output will not reach to overwrite and will fuck up all the stats
    guard.len(doku.rows, doku.sheet.rows, "Doku rows")

    for row in doku.sheet.rows:
        with message_guardian(guard, doku.get_id(row)):
            if doku.is_shiny(row):
                guard.sniff(doku.is_caught(row), "Uncaught shiny")


@message_guardian(guard)
def validate_doku_diffs(doku: Doku, diffs: DokuDiffs):
    for row in doku.sheet.rows:
        poke_id = doku.get_id(row)
        with message_guardian(guard, poke_id):
            if doku.is_shiny(row):
                poke_id += "*"
            guard.eq(doku.is_caught(row), poke_id in diffs.out_caught, "Caught not in out")

    categories: Dict[str, DokuDiff] = {}
    for puzzle in diffs.puzzles:
        for diff in puzzle.diffs:
            with message_guardian(guard, diff.message):
                guard.bark.nonside(diff.category, categories, 'Duplicate category')
                guard.nonside(diff.reverse, categories, 'Duplicate reverse')
                categories[diff.category] = diff

                if diff.category != "All / All":
                    guard.uneq(diff.category, diff.reverse, "Invalid equal categories")

    for diff in diffs.stats_diffs:
        with message_guardian(guard, diff.message):
            if diff.total == 0:
                guard.bark.eq(diff.remaining, 0, "Remaining without total")
                guard.bark_if(diffs.seen(diff), "Seen without total")
            else:
                guard.bark.eq(diff.remaining == 0, diffs.seen(diff), "Seen while remaining")

            out_diff = categories.get(diff.category) or categories.get(diff.reverse)
            if out_diff:
                with message_guardian(guard, out_diff.message):
                    guard.bark.sniff(out_diff.remaining == 0 and diff.remaining == 0, "Nonzero remaining")
                    guard.bark.eq(out_diff.total, diff.total, "Mismatched totals")
                    guard.bark.positive(diff.total, "Out without total")


def run_validation(db: Database, dex: Dex, doku: Doku, diffs: DokuDiffs):
    validate_command_out(db)
    validate_db(db)
    validate_dex(db, dex.sheet)
    validate_doku(doku)
    validate_doku_diffs(doku, diffs)
