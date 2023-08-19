from typing import Dict

from main.pokehome.constants.pokes import REGIONS
from main.pokehome.constants.sheets import DexFields, EMPTY_ABILITY, HiddenAbilityProgress, get_dex_sheet, \
    SAME_ID_DIFFERENT_FIELDS
from main.pokehome.db import Database
from main.util.data import Sheet


def validate_dex(db: Database, sheet: Sheet):
    id_map: Dict[str, int] = {}
    hidden_families: Dict[str, bool] = {}

    for index, row in enumerate(sheet.rows):
        def get(field: DexFields) -> str:
            return sheet.get(row, field.value)

        name = get(DexFields.NAME)
        row_id = get(DexFields.ID)
        db_row = db.get(row_id)

        caught: bool = get(DexFields.CAUGHT_PROGRESS) == "TRUE"
        nickname = get(DexFields.NICKNAME)
        if nickname and not caught and not nickname.startswith("TODO"):
            print(f"Uncaught with nickname {nickname} for {name}")

        trainer = get(DexFields.TRAINER)
        if trainer and not caught:
            print(f"Uncaught with trainer {trainer} for {name}")
        if caught and not trainer:
            print(f"Caught without trainer for {name}")

        region = get(DexFields.REGION)
        assert region in REGIONS

        hidden_ability = get(DexFields.HIDDEN_ABILITY)
        hidden_progress = get(DexFields.HIDDEN_PROGRESS)
        assert db_row.hidden == hidden_ability
        assert hidden_progress in [e for e in HiddenAbilityProgress]
        if hidden_ability == EMPTY_ABILITY or name == "Pangoro":
            assert hidden_progress == HiddenAbilityProgress.NO_HIDDEN_ABILITY
        else:
            has_hidden = hidden_progress != HiddenAbilityProgress.UNOBTAINED
            if hidden_families.get(db_row.family, has_hidden) != has_hidden:
                print(f"Hidden ability does not match family for {name}")
            hidden_families[db_row.family] = has_hidden

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
