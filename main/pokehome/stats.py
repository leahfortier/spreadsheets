from typing import List, Dict, Tuple

from main.pokehome.constants.io import STATS_OUTFILE, DOKU_STATS_OUTFILE
from main.pokehome.constants.pokes import REGIONS, CURRENT_GENERATION, ALL_TYPES
from main.pokehome.constants.sheets import DexFields, HiddenAbilityProgress, DEX_TAB, DexClassification, DokuFields, \
    DOKU_TAB, EvolutionType, EMPTY_FIELD
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv
from main.util.sheets_formulas import Progress, progress_difference
from pokehome.doku import Doku
from util.sheets_conditions import Column


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


class DokuStats:
    def __init__(self, doku: Doku):
        self.out = OutStatsVertical()
        self.doku = doku

        self.caught_col = self.col(DokuFields.DEX).with_checkbox()
        self.missing_col = self.col(DokuFields.DEX).with_false_checkbox()
        self.shiny_col = self.col(DokuFields.SHINY).with_checkbox()

        self.mono_col = self.col(DokuFields.TYPE2).with_string(EMPTY_FIELD)
        self.dual_col = self.col(DokuFields.TYPE2).with_string("<>" + EMPTY_FIELD)

        self.type_cols: Dict[str, Tuple[Column, Column]] = {}
        for poke_type in ALL_TYPES:
            type1_col = self.col(DokuFields.TYPE1).with_string(poke_type)
            type2_col = self.col(DokuFields.TYPE2).with_string(poke_type)
            self.type_cols[poke_type] = type1_col, type2_col

    def col(self, field: DokuFields) -> Column:
        return Column(self.doku.sheet, DOKU_TAB, field)

    def get_values(self, *conditions: str) -> List[str]:
        caught_vals = self.caught_col.progress(*conditions)
        missing_vals = self.missing_col.progress(*conditions)
        shiny_vals = self.shiny_col.progress(*conditions)

        mono_vals = self.missing_col.progress(*conditions, self.mono_col.condition)
        dual_vals = self.missing_col.progress(*conditions, self.dual_col.condition)

        all_type_vals = []
        for poke_type in ALL_TYPES:
            type1_col, type2_col = self.type_cols[poke_type]
            type1_vals = self.missing_col.progress(*conditions, type1_col.condition)
            type2_vals = self.missing_col.progress(*conditions, type2_col.condition)
            all_type_vals.append(type1_vals.with_or(type2_vals))

        return get_values_from_progress(caught_vals, missing_vals, shiny_vals, mono_vals, dual_vals, all_type_vals)

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
        def get_dual_type_progress(primary_type: str, secondary_type: str) -> Progress:
            primary_col = self.col(DokuFields.TYPE1).with_string(primary_type)
            secondary_col = self.col(DokuFields.TYPE2).with_string(secondary_type)
            return self.missing_col.progress(primary_col.condition, secondary_col.condition)

        for poke_type in ALL_TYPES:
            type1_col, type2_col = self.type_cols[poke_type]

            is_primary_type = type1_col.condition
            is_secondary_type = type2_col.condition

            caught_vals = self.caught_col.or_progress(is_primary_type, is_secondary_type)
            missing_vals = self.missing_col.or_progress(is_primary_type, is_secondary_type)
            shiny_vals = self.shiny_col.or_progress(is_primary_type, is_secondary_type)

            mono_vals = get_dual_type_progress(poke_type, EMPTY_FIELD)
            dual_vals = progress_difference(missing_vals, mono_vals)

            all_type_vals = []
            for dual_type in ALL_TYPES:
                primary_vals = get_dual_type_progress(poke_type, dual_type)
                secondary_vals = get_dual_type_progress(dual_type, poke_type)

                dual_type_vals = primary_vals.with_or(secondary_vals)
                all_type_vals.append(dual_type_vals)

            values = get_values_from_progress(caught_vals, missing_vals, shiny_vals, mono_vals, dual_vals, all_type_vals)
            self.out.append(poke_type, values)

    def append_special(self):
        self.out.append("Mono-Type", self.get_values(self.mono_col.condition))
        self.out.append("Dual-Type", self.get_values(self.dual_col.condition))

        branch_col = self.col(DokuFields.BRANCH_EVO).with_string("Yes")
        self.out.append("Has Branch", self.get_values(branch_col.condition))

        evolution_col = self.col(DokuFields.EVO_TYPE)
        for evo_type in EvolutionType:
            evolution_col.with_string(evo_type)
            self.out.append(evo_type, self.get_values(evolution_col.condition))


def get_values_from_progress(
        caught_vals: Progress,
        missing_vals: Progress,
        shiny_vals: Progress,
        mono_vals: Progress,
        dual_vals: Progress,
        all_type_vals: List[Progress],
) -> List[str]:
    return [
        caught_vals.concatenated, shiny_vals.count,
        missing_vals.count, mono_vals.concatenated, dual_vals.concatenated,
        caught_vals.percent, shiny_vals.percent, mono_vals.percent, dual_vals.percent,
        *[type_vals.concatenated for type_vals in all_type_vals]
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
