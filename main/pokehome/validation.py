from typing import Dict, List, Set

from main.pokehome.constants.io import ABILITIES_OUTFILE, REGIONS_OUTFILE, FAMILIES_OUTFILE, GENDER_OUTFILE, \
    BALLS_OUTFILE
from main.pokehome.constants.pokes import REGIONS, INCLUDE_UNBREEDABLE_POKEBALLS, BALL_NOTES
from main.pokehome.constants.sheets import DexFields, EMPTY_ABILITY, HiddenAbilityProgress, get_dex_sheet, \
    SAME_ID_DIFFERENT_FIELDS
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex, DexRow
from main.util.data import Sheet
from main.util.file_io import from_tsv, to_file


def validate_dex(db: Database, sheet: Sheet):
    id_map: Dict[str, int] = {}
    hidden_families: Dict[str, bool] = {}
    ball_families: Dict[str, Set[str]] = {}
    ball_map: Dict[str, List[str]] = {}

    main_fields = [field.value for field in DexFields]
    ball_fields = [field for field in sheet.schema_row if field not in main_fields]

    for index, row in enumerate(sheet.rows):
        def get(field: DexFields) -> str:
            return sheet.get(row, field.value)

        def is_caught(field: str) -> bool:
            return sheet.get(row, field) == "TRUE"

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
        if hidden_ability == EMPTY_ABILITY or name == "Pangoro":
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


def validate_command_out(db: Database):
    db_rows: List[DbRow] = db.rows
    ability_rows: List[List[str]] = from_tsv(ABILITIES_OUTFILE)
    region_rows: List[List[str]] = from_tsv(REGIONS_OUTFILE)
    evolution_rows: List[List[str]] = from_tsv(FAMILIES_OUTFILE)
    gender_rows: List[List[str]] = from_tsv(GENDER_OUTFILE)

    # Rows must correspond to each other
    assert len(ability_rows) == len(db_rows)
    assert len(region_rows) == len(db_rows)
    assert len(evolution_rows) == len(db_rows)
    assert len(gender_rows) == len(db_rows)

    for index, row in enumerate(db_rows):
        # If this fails you need to either:
        #  - Update the respective DB columns with the output file
        #  - Update the input file with new data to match
        assert ability_rows[index] == [row.ability1, row.ability2, row.hidden]
        assert region_rows[index] == [row.region]
        assert evolution_rows[index] == [row.family]
        assert gender_rows[index] == [row.can_breed_field, row.gender_ratio]


def run_validation(db: Database, dex: Dex):
    validate_command_out(db)
    validate_dex(db, dex.sheet)
