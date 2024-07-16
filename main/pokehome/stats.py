from enum import Enum
from typing import List, Optional, Self, Generic, TypeVar, Callable

from main.pokehome.constants.io import STATS_OUTFILE, DOKU_STATS_OUTFILE
from main.pokehome.constants.pokes import REGIONS, CURRENT_GENERATION, ALL_TYPES
from main.pokehome.constants.sheets import DexFields, HiddenAbilityProgress, DEX_TAB, DexClassification, DokuFields, \
    DOKU_TAB, EvolutionType, EMPTY_FIELD
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv
from main.util.sheets_formulas import caught_total_progress, count_with_percentage, condition_as_count, column_range, \
    or_caught_total_progress
from pokehome.doku import Doku
from util.data import Sheet

FieldsEnum = TypeVar("FieldsEnum", bound=Enum)


class Column(Generic[FieldsEnum]):
    def __init__(self, sheet: Sheet, tab: str, field: FieldsEnum):
        self.start_index = 2
        self.col_range = column_range(sheet.column(field), self.start_index, tab=tab)

    def _with_value(self, value: str) -> Self:
        self.value = value
        self.condition = f"{self.col_range}, {self.value}"
        return self

    def with_string(self, value: str) -> Self:
        if isinstance(value, Enum):
            value = value.value
        return self._with_value(f'"{value}"')

    def with_checkbox(self) -> Self:
        return self._with_value("TRUE")

    def progress(self, *conditions: str) -> str:
        return condition_as_count(self.condition, *conditions)

    def caught_total_progress(self, *conditions: str) -> List[str]:
        return caught_total_progress(self.condition, *conditions)

    def or_caught_total_progress(self, first_condition: str, second_condition: str) -> List[str]:
        return or_caught_total_progress(self.condition, first_condition, second_condition)


class OutStats:
    def __init__(self):
        self.rows: List[List[str]] = []
        self.column_index = 0
        self.index = 0

    def new_column(self):
        self.column_index += 1
        self.index = 0

    def append(self, name: str, values: List[str]):
        values.insert(0, name)

        if self.index == len(self.rows):
            self.rows.append([""]*(self.column_index * (len(values) + 1)))
        elif self.column_index > 0:
            self.rows[self.index] += [""*self.column_index]

        self.rows[self.index] += values
        self.index += 1


def get_dex_stats(dex: Dex):
    def col(field: DexFields) -> Column:
        return Column(dex.sheet, DEX_TAB, field)

    caught_col = col(DexFields.CAUGHT_PROGRESS).with_checkbox()
    hidden_col = col(DexFields.HIDDEN_PROGRESS).with_string("<>" + HiddenAbilityProgress.UNOBTAINED)
    nickname_col = col(DexFields.NICKNAME).with_string("<>")
    shiny_col = col(DexFields.SHINY).with_checkbox()

    def get_values(*conditions: str) -> List[str]:
        have_values = caught_col.caught_total_progress(*conditions)
        hidden_value = hidden_col.progress(*conditions)
        nickname_value = nickname_col.progress(*conditions)
        shiny_value = shiny_col.progress(*conditions)
        return [*have_values, hidden_value, nickname_value, shiny_value]

    out: OutStats = OutStats()
    out.append("All", get_values())

    class_col = col(DexFields.CLASS)
    for classification in DexClassification:
        class_col.with_string(classification)
        out.append(classification, get_values(class_col.condition))
    out.new_column()

    box_col = col(DexFields.BOX)
    for box in dex.boxes.boxes:
        box_col.with_string(box.name)
        out.append(box.name, get_values(box_col.condition))
    out.new_column()

    region_col = col(DexFields.REGION)
    for region in REGIONS:
        region_col.with_string(region)
        out.append(region, get_values(region_col.condition))
    out.new_column()

    to_tsv(STATS_OUTFILE, out.rows)


def get_doku_stats(doku: Doku):
    def col(field: DokuFields) -> Column:
        return Column(doku.sheet, DOKU_TAB, field)

    dex_col = col(DokuFields.DEX).with_checkbox()

    def get_values(*conditions: str) -> List[str]:
        return dex_col.caught_total_progress(*conditions)

    def get_values_or(first_condition: str, second_condition: str) -> List[str]:
        return dex_col.or_caught_total_progress(first_condition, second_condition)

    out: OutStats = OutStats()
    out.append("All", get_values())

    generation_col = col(DokuFields.GENERATION)
    for gen in range(1, CURRENT_GENERATION + 1):
        generation_col.with_string(str(gen))
        out.append(f"Gen {gen}", get_values(generation_col.condition))
    out.new_column()

    region_col = col(DokuFields.REGION)
    for region in REGIONS:
        region_col.with_string(region)
        out.append(region, get_values(region_col.condition))
    out.new_column()

    type1_col = col(DokuFields.TYPE1)
    type2_col = col(DokuFields.TYPE2)
    for poke_type in ALL_TYPES:
        type1_col.with_string(poke_type)
        type2_col.with_string(poke_type)
        out.append(poke_type, get_values_or(type1_col.condition, type2_col.condition))
    out.new_column()

    type2_col.with_string(EMPTY_FIELD)
    out.append("Mono-Type", get_values(type2_col.condition))

    type2_col.with_string("<>" + EMPTY_FIELD)
    out.append("Dual-Type", get_values(type2_col.condition))

    branch_col = col(DokuFields.BRANCH_EVO).with_string("Yes")
    out.append("Has Branch", get_values(branch_col.condition))

    evolution_col = col(DokuFields.EVO_TYPE)
    for evo_type in EvolutionType:
        evolution_col.with_string(evo_type)
        out.append(evo_type, get_values(evolution_col.condition))

    to_tsv(DOKU_STATS_OUTFILE, out.rows)


def write_stats(dex: Dex, doku: Doku):
    get_dex_stats(dex)
    get_doku_stats(doku)