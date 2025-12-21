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
from util.general import all_unique, to_str, warn, warn_if


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

        # Uncaught Pokemon should not have a nickname or OT
        if nickname and not caught and not nickname.startswith("TODO"):
            print(f"Uncaught with nickname {nickname} for {name}")
        if trainer and not caught:
            print(f"Uncaught with trainer {trainer} for {name}")

        # All caught Pokemon should include their OT
        if caught and not trainer:
            print(f"Caught without trainer for {name}")

        # Validate region
        region = get(DexFields.REGION)
        assert region in REGIONS

        # Hidden ability matches family or N/A
        assert db_row.hidden == hidden_ability
        assert hidden_progress in [e for e in HiddenAbilityProgress]
        if hidden_ability == EMPTY_FIELD or name == "Pangoro":
            assert hidden_progress == HiddenAbilityProgress.NO_HIDDEN_ABILITY
        else:
            has_hidden = hidden_progress != HiddenAbilityProgress.UNOBTAINED
            if hidden_families.get(db_row.family, has_hidden) != has_hidden:
                print(f"{name}: Hidden ability ({hidden_progress}) does not match family ({not has_hidden})")
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
                    assert form_value != base_value
                elif form_value != base_value:
                    print(f"Mismatched field {field} (Base: {base_value}, Form: {form_value}) for {row_id}: {row}")
        else:
            id_map[row_id] = index

            for ball in ball_fields:
                if is_caught(ball):
                    ball_map.setdefault(ball, [])
                    ball_map.get(ball).append(name)

                    # Assert only one family member per ball
                    ball_families.setdefault(family, set())
                    if ball in ball_families.get(family):
                        print(f"Duplicate {ball} Ball for {family}")
                    ball_families[family].add(ball)

                    # Only collecting balls for Pokemon that can pass them down
                    if not db_row.can_breed() and db_row.species not in INCLUDE_UNBREEDABLE_POKEBALLS:
                        print(f"{ball} Ball marked for Unbreedable Pokemon {name}")

    for ball in BALL_NOTES.keys():
        assert ball in ball_map

    out: List[str] = []
    for ball, names in ball_map.items():
        out.append(f"{ball}: {len(names)}{BALL_NOTES.get(ball, '')}")
        for name in names:
            out.append("\t" + name)
        out.append("")
    to_file(BALLS_OUTFILE, out)


def validate_db(db: Database):
    fossil_families: Dict[str, bool] = {}
    for row in db.rows:
        # Baby Pokemon must be first in evolution
        if row.is_baby():
            assert row.evolution_type == EvolutionType.FIRST, row.name

        # Fossil status must be consistent for all family members
        fossil = row.is_fossil()
        if fossil_families.get(row.family, fossil) != fossil:
            warn(f"{row.name}: Fossil status does not match family")
        fossil_families[row.family] = fossil


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
    assert len(ability_rows) == len(db_rows)
    assert len(type_rows) == len(db_rows)
    assert len(region_rows) == len(db_rows)
    assert len(evolution_rows) == len(db_rows)
    assert len(gender_rows) == len(db_rows)
    assert len(category_rows) == len(db_rows)

    assert len(sheet_rows) == len(db_rows)

    for index, row in enumerate(db_rows):
        # If this fails you need to either:
        #  - Update the respective DB columns with the output file
        #  - Update the input file with new data to match
        assert ability_rows[index] == [row.ability1, row.ability2, row.hidden]
        assert type_rows[index] == [row.type1, row.type2]
        assert region_rows[index] == [row.generation, row.region]
        assert evolution_rows[index] == [row.has_branch_evo, row.evolution_type, row.family]
        assert gender_rows[index] == [row.can_breed_field, row.gender_ratio]
        assert category_rows[index] == [row.baby, row.fossil, row.partner, row.legendary, row.mythical, row.paradox, row.ultra]

        assert row.ability1 != EMPTY_FIELD and all_unique(ability_rows[index], exceptions=[EMPTY_FIELD])
        assert row.type1 != EMPTY_FIELD and all_unique(type_rows[index])
        assert row.region in REGIONS
        sheet_row = sheet_rows[index]

        def print_mismatch(label: str, sheet_fields: List[DbFields], row_values: List[str]):
            sheet_values = [db.sheet.get(sheet_row, field) for field in sheet_fields]
            if sheet_values != row_values:
                warn(f"{label} mismatch for {row.name}: {sheet_values} {row_values}")

        print_mismatch("Ability", [DbFields.ABILITY1, DbFields.ABILITY2, DbFields.HIDDEN_ABILITY], ability_rows[index])
        print_mismatch("Type", [DbFields.TYPE1, DbFields.TYPE2], type_rows[index])
        print_mismatch("Region", [DbFields.GENERATION, DbFields.OG_REGION], region_rows[index])
        print_mismatch("Family", [DbFields.HAS_BRANCH, DbFields.EVO_TYPE, DbFields.FAMILY_EVOS], evolution_rows[index])
        print_mismatch("Gender", [DbFields.CAN_BREED, DbFields.GENDER_RATIO], gender_rows[index])
        print_mismatch("Category", [DbFields.IS_BABY, DbFields.IS_FOSSIL, DbFields.IS_PARTNER, DbFields.IS_LEGENDARY, DbFields.IS_MYTHICAL, DbFields.IS_PARADOX, DbFields.IS_ULTRA_BEAST], category_rows[index])


def validate_doku(doku: Doku):
    expected_rows = len(doku.rows)
    actual_rows = len(doku.sheet.rows)

    # Accidentally added a bunch of extra rows once by trying to update doku fields from db
    # You will need to manually delete the extra rows at the bottom of the file since correctly
    #   pasting doku output will not reach to overwrite and will fuck up all the stats
    assert expected_rows == actual_rows, f'{expected_rows} != {actual_rows}'


def validate_doku_diffs(diffs: DokuDiffs):
    categories: Dict[str, DokuDiff] = {}
    for diff in diffs.out_diffs:
        assert diff.category not in categories, diff.message
        warn_if(diff.reverse in categories, f'Duplicate diff entry: {diff.message}')
        categories[diff.category] = diff

        assert diff.category != diff.reverse, diff.message

    for diff in diffs.stats_diffs:
        if diff.total == 0:
            assert diff.remaining == 0, diff.message
            assert not diffs.seen(diff), diff.message
        else:
            assert (diff.remaining == 0) == diffs.seen(diff), diff.message

        out_diff = categories.get(diff.category) or categories.get(diff.reverse)
        if out_diff:
            assert out_diff.remaining == 0 and diff.remaining == 0, diff.message
            assert out_diff.total == diff.total and diff.total > 0, f'{out_diff.total} != {diff.total} | {diff.message}'


def run_validation(db: Database, dex: Dex, doku: Doku):
    validate_command_out(db)
    validate_db(db)
    validate_dex(db, dex.sheet)
    validate_doku(doku)
    validate_doku_diffs(doku.diffs)
