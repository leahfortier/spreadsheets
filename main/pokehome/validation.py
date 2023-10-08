from typing import Dict, List, Set

from main.pokehome.constants.io import ABILITIES_OUTFILE, REGIONS_OUTFILE, EVOLUTIONS_OUTFILE
from main.pokehome.constants.pokes import REGIONS
from main.pokehome.constants.sheets import DexFields, EMPTY_ABILITY, HiddenAbilityProgress, get_dex_sheet, \
    SAME_ID_DIFFERENT_FIELDS
from main.pokehome.db import Database, DbRow
from main.pokehome.dex import Dex, DexRow
from main.util.data import Sheet
from main.util.file_io import from_tsv


def validate_dex(db: Database, sheet: Sheet):
    id_map: Dict[str, int] = {}
    hidden_families: Dict[str, bool] = {}
    ball_families: Dict[str, Set[str]] = {}

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

        # Assert only one family member per ball
        for ball in ball_fields:
            if is_caught(ball):
                ball_families.setdefault(family, set())
                if ball in ball_families.get(family):
                    print(f"Duplicate {ball} Ball for {family}")
                ball_families[family].add(ball)

        # Hidden ability matches family or N/A
        assert db_row.hidden == hidden_ability
        assert hidden_progress in [e for e in HiddenAbilityProgress]
        if hidden_ability == EMPTY_ABILITY or name == "Pangoro":
            assert hidden_progress == HiddenAbilityProgress.NO_HIDDEN_ABILITY
        else:
            has_hidden = hidden_progress != HiddenAbilityProgress.UNOBTAINED
            if hidden_families.get(db_row.family, has_hidden) != has_hidden:
                print(f"Hidden ability does not match family for {name}")
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


def validate_command_out(db: Database):
    db_rows: List[DbRow] = db.rows
    ability_rows: List[List[str]] = from_tsv(ABILITIES_OUTFILE)
    region_rows: List[List[str]] = from_tsv(REGIONS_OUTFILE)
    evolution_rows: List[List[str]] = from_tsv(EVOLUTIONS_OUTFILE)

    assert len(ability_rows) == len(db_rows)
    assert len(region_rows) == len(db_rows)
    assert len(evolution_rows) == len(db_rows)
    for index, row in enumerate(db_rows):
        assert ability_rows[index] == [row.ability1, row.ability2, row.hidden]
        assert region_rows[index] == [row.region]
        assert evolution_rows[index] == [row.family]


def run_validation(db: Database, dex: Dex):
    validate_command_out(db)
    validate_dex(db, dex.sheet)
