from typing import Dict

from main.pokehome.constants.pokes import REGIONS
from main.pokehome.constants.sheets import DexFields, EMPTY_ABILITY, HiddenAbilityProgress, get_dex_sheet, \
    SAME_ID_DIFFERENT_FIELDS
from main.util.data import Sheet


def validate_dex(sheet: Sheet):
    id_map: Dict[str, int] = {}
    for index, row in enumerate(sheet.rows):
        def get(field: DexFields) -> str:
            return sheet.get(row, field.value)

        caught: bool = get(DexFields.CAUGHT_PROGRESS) == "TRUE"
        nickname = get(DexFields.NICKNAME)
        if nickname and not caught:
            print(f"Uncaught with nickname {nickname}")

        region = get(DexFields.REGION)
        assert region in REGIONS

        hidden_ability = get(DexFields.HIDDEN_ABILITY)
        hidden_progress = get(DexFields.HIDDEN_PROGRESS)
        if hidden_ability == EMPTY_ABILITY:
            assert hidden_progress == HiddenAbilityProgress.NO_HIDDEN_ABILITY
        assert hidden_progress in [e for e in HiddenAbilityProgress]

        row_id = get(DexFields.ID)
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
