from enum import Enum
from typing import List, Self, Generic, TypeVar

from main.pokehome.constants.io import STATS_OUTFILE, DOKU_STATS_OUTFILE
from main.pokehome.constants.pokes import REGIONS, CURRENT_GENERATION, ALL_TYPES
from main.pokehome.constants.sheets import DexFields, HiddenAbilityProgress, DEX_TAB, DexClassification, DokuFields, \
    DOKU_TAB, EvolutionType, EMPTY_FIELD, DokuFormType
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv
from main.util.sheets_formulas import caught_total_progress, column_range, \
    or_caught_total_progress, Progress, progress_difference
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

    def with_false_checkbox(self) -> Self:
        return self._with_value("FALSE")

    def count(self, *conditions: str) -> str:
        return caught_total_progress(self.condition, *conditions).count

    def progress(self, *conditions: str) -> Progress:
        return caught_total_progress(self.condition, *conditions)

    def or_progress(self, first_condition: str, second_condition: str) -> Progress:
        return or_caught_total_progress(self.condition, first_condition, second_condition)


class OutStatsHorizontal:
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
            self.rows.append([""] * (self.column_index * (len(values) + 1)))
        elif self.column_index > 0:
            self.rows[self.index] += ["" * self.column_index]

        self.rows[self.index] += values
        self.index += 1


class OutStatsVertical:
    def __init__(self):
        self.rows: List[List[str]] = []

    def blank_row(self):
        self.rows.append([""] * len(self.rows[0]))

    def append(self, name: str, values: List[str]):
        values.insert(0, name)
        self.rows.append(values)


def get_dex_stats(dex: Dex):
    def col(field: DexFields) -> Column:
        return Column(dex.sheet, DEX_TAB, field)

    caught_col = col(DexFields.CAUGHT_PROGRESS).with_checkbox()
    hidden_col = col(DexFields.HIDDEN_PROGRESS).with_string("<>" + HiddenAbilityProgress.UNOBTAINED)
    nickname_col = col(DexFields.NICKNAME).with_string("<>")
    shiny_col = col(DexFields.SHINY).with_checkbox()

    def get_values(*conditions: str) -> List[str]:
        have_values = caught_col.progress(*conditions).values()
        hidden_value = hidden_col.count(*conditions)
        nickname_value = nickname_col.count(*conditions)
        shiny_value = shiny_col.count(*conditions)
        return [*have_values, hidden_value, nickname_value, shiny_value]

    out = OutStatsHorizontal()
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


class DokuStatsRow:
    def __init__(self, name: str):
        self.values = []


class DokuStats:
    def __init__(self, doku: Doku):
        self.out = OutStatsVertical()
        self.doku = doku

        self.caught_col = self.col(DokuFields.DEX).with_checkbox()
        self.missing_col = self.col(DokuFields.DEX).with_false_checkbox()
        self.shiny_col = self.col(DokuFields.SHINY).with_checkbox()
        self.mono_col = self.col(DokuFields.TYPE2).with_string(EMPTY_FIELD)
        self.dual_col = self.col(DokuFields.TYPE2).with_string("<>" + EMPTY_FIELD)

        self.type1_col = self.col(DokuFields.TYPE1)
        self.type2_col = self.col(DokuFields.TYPE2)

    def col(self, field: DokuFields) -> Column:
        return Column(self.doku.sheet, DOKU_TAB, field)

    def get_values(self, *conditions: str) -> List[str]:
        caught_vals = self.caught_col.progress(*conditions)
        missing_vals = self.missing_col.progress(*conditions)
        shiny_vals = self.shiny_col.progress(*conditions)
        mono_vals = self.missing_col.progress(*conditions, self.mono_col.condition)
        dual_vals = self.missing_col.progress(*conditions, self.dual_col.condition)
        return get_values_from_progress(caught_vals, missing_vals, shiny_vals, mono_vals, dual_vals)

    def append_full(self):
        self.out.append("All", self.get_values())

    def append_generations(self):
        generation_col = self.col(DokuFields.GENERATION)
        for gen in range(1, CURRENT_GENERATION + 1):
            generation_col.with_string(str(gen))
            self.out.append(f"Gen {gen}", self.get_values(generation_col.condition))

    def append_regions(self):
        region_col = self.col(DokuFields.REGION)
        for region in REGIONS:
            region_col.with_string(region)
            self.out.append(region, self.get_values(region_col.condition))

    def append_types(self):
        for poke_type in ALL_TYPES:
            self.type1_col.with_string(poke_type)
            self.type2_col.with_string(poke_type)

            is_primary_type = self.type1_col.condition
            is_secondary_type = self.type2_col.condition

            caught_vals = self.caught_col.or_progress(is_primary_type, is_secondary_type)
            missing_vals = self.missing_col.or_progress(is_primary_type, is_secondary_type)
            shiny_vals = self.shiny_col.or_progress(is_primary_type, is_secondary_type)

            mono_vals = self.caught_col.progress(self.type1_col.condition, self.mono_col.condition)
            dual_vals = progress_difference(missing_vals, mono_vals)

            values = get_values_from_progress(caught_vals, missing_vals, shiny_vals, mono_vals, dual_vals)

            self.out.append(poke_type, values)

    def append_special(self):
        self.type2_col.with_string(EMPTY_FIELD)
        self.out.append("Mono-Type", self.get_values(self.type2_col.condition))

        self.type2_col.with_string("<>" + EMPTY_FIELD)
        self.out.append("Dual-Type", self.get_values(self.type2_col.condition))

        branch_col = self.col(DokuFields.BRANCH_EVO).with_string("Yes")
        self.out.append("Has Branch", self.get_values(branch_col.condition))

        evolution_col = self.col(DokuFields.EVO_TYPE)
        for evo_type in EvolutionType:
            evolution_col.with_string(evo_type)
            self.out.append(evo_type, self.get_values(evolution_col.condition))

        form_col = self.col(DokuFields.FORM)
        form_col.with_string(DokuFormType.MEGA)
        self.out.append("Mega", self.get_values(form_col.condition))
        form_col.with_string(DokuFormType.GMAX)
        self.out.append("Gmax", self.get_values(form_col.condition))


def get_values_from_progress(
        caught_vals: Progress,
        missing_vals: Progress,
        shiny_vals: Progress,
        mono_vals: Progress,
        dual_vals: Progress
) -> List[str]:
    return [
        caught_vals.concatenated, shiny_vals.count,
        missing_vals.count, mono_vals.concatenated, dual_vals.concatenated,
        caught_vals.percent, shiny_vals.percent, mono_vals.percent, dual_vals.percent
    ]


def get_doku_stats(doku: Doku):
    stats = DokuStats(doku)

    stats.append_full()
    stats.out.blank_row()

    stats.append_generations()
    stats.out.blank_row()

    stats.append_regions()
    stats.out.blank_row()

    stats.append_types()
    stats.out.blank_row()

    stats.append_special()

    to_tsv(DOKU_STATS_OUTFILE, stats.out.rows)


def write_stats(dex: Dex, doku: Doku):
    get_dex_stats(dex)
    get_doku_stats(doku)
