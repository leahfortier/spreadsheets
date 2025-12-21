from typing import List, Dict, Tuple

from main.pokehome.constants.io import STATS_OUTFILE, DOKU_STATS_OUTFILE
from main.pokehome.constants.pokes import REGIONS, CURRENT_GENERATION, ALL_TYPES
from main.pokehome.constants.sheets import DexFields, HiddenAbilityProgress, DEX_TAB, DexClassification, DokuFields, \
    DOKU_TAB, EvolutionType, EMPTY_FIELD, DB_TRUE
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv
from main.util.sheets_formulas import Progress, progress_difference
from pokehome.doku import Doku
from util.sheets_conditions import Column, ColumnBuilder


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


def write_dex_stats(dex: Dex):
    def col(field: DexFields) -> ColumnBuilder:
        return ColumnBuilder(dex.sheet, DEX_TAB, field)

    caught_col = col(DexFields.CAUGHT_PROGRESS).with_checkbox().build()
    hidden_col = col(DexFields.HIDDEN_PROGRESS).with_string("<>" + HiddenAbilityProgress.UNOBTAINED).build()
    nickname_col = col(DexFields.NICKNAME).with_string("<>").build()
    shiny_col = col(DexFields.SHINY).with_checkbox().build()

    def get_values(*conditions: str) -> List[str]:
        have_values = caught_col.progress(*conditions).values()
        hidden_value = hidden_col.count(*conditions)
        nickname_value = nickname_col.count(*conditions)
        shiny_value = shiny_col.count(*conditions)
        return [*have_values, hidden_value, nickname_value, shiny_value]

    out = OutStatsHorizontal()
    out.append("All", get_values())

    for classification in DexClassification:
        class_col = col(DexFields.CLASS).with_string(classification).build()
        out.append(classification, get_values(class_col.condition))
    out.new_column()

    for box in dex.boxes.boxes:
        box_col = col(DexFields.BOX).with_string(box.name).build()
        out.append(box.name, get_values(box_col.condition))
    out.new_column()

    for region in REGIONS:
        region_col = col(DexFields.REGION).with_string(region).build()
        out.append(region, get_values(region_col.condition))
    out.new_column()

    to_tsv(STATS_OUTFILE, out.rows)


class DokuStats:
    def __init__(self, doku: Doku):
        self.out = OutStatsVertical()
        self.doku = doku

        self.caught_col = self.col(DokuFields.DEX).with_checkbox().build()
        self.missing_col = self.col(DokuFields.DEX).with_false_checkbox().build()
        self.shiny_col = self.col(DokuFields.SHINY).with_checkbox().build()

        self.mono_col = self.col(DokuFields.TYPE2).with_string(EMPTY_FIELD).build()
        self.dual_col = self.col(DokuFields.TYPE2).with_string("<>" + EMPTY_FIELD).build()

        self.type_cols: Dict[str, Tuple[Column, Column]] = {}
        for poke_type in ALL_TYPES:
            type1_col = self.col(DokuFields.TYPE1).with_string(poke_type).build()
            type2_col = self.col(DokuFields.TYPE2).with_string(poke_type).build()
            self.type_cols[poke_type] = type1_col, type2_col

        self.evo_cols: Dict[str, Column] = {}
        for evo_type in EvolutionType:
            evolution_col = self.col(DokuFields.EVO_TYPE).with_string(evo_type).build()
            self.evo_cols[evo_type] = evolution_col

        def get_bool_col(column: DokuFields) -> Column:
            return self.col(column).with_string(DB_TRUE).build()

        self.branch_col = get_bool_col(DokuFields.HAS_BRANCH)
        self.baby_col = get_bool_col(DokuFields.IS_BABY)
        self.fossil_col = get_bool_col(DokuFields.IS_FOSSIL)
        self.partner_col = get_bool_col(DokuFields.IS_PARTNER)
        self.legend_col = get_bool_col(DokuFields.IS_LEGENDARY)
        self.mythic_col = get_bool_col(DokuFields.IS_MYTHICAL)
        self.paradox_col = get_bool_col(DokuFields.IS_PARADOX)
        self.ultra_col = get_bool_col(DokuFields.IS_ULTRA_BEAST)

        self.extra_cols = []
        for evo_type in EvolutionType:
            self.extra_cols.append(self.evo_cols[evo_type])
        self.extra_cols.append(self.partner_col)
        self.extra_cols.append(self.legend_col)

    def col(self, field: DokuFields) -> ColumnBuilder:
        return ColumnBuilder(self.doku.sheet, DOKU_TAB, field)

    def get_type_progress(self, poke_type: str, *conditions: str) -> Progress:
        type1_col, type2_col = self.type_cols[poke_type]
        type1_vals = self.missing_col.progress(*conditions, type1_col.condition)
        type2_vals = self.missing_col.progress(*conditions, type2_col.condition)
        return type1_vals.with_or(type2_vals)

    def get_values(self, *conditions: str) -> List[str]:
        caught_vals = self.caught_col.progress(*conditions)
        missing_vals = self.missing_col.progress(*conditions)
        shiny_vals = self.shiny_col.progress(*conditions)

        mono_vals = self.missing_col.progress(*conditions, self.mono_col.condition)
        dual_vals = self.missing_col.progress(*conditions, self.dual_col.condition)

        all_type_vals = [self.get_type_progress(poke_type, *conditions) for poke_type in ALL_TYPES]
        extra_vals = [self.missing_col.progress(*conditions, extra_col.condition) for extra_col in self.extra_cols]

        return get_values_from_progress(
            caught_vals, missing_vals, shiny_vals,
            mono_vals, dual_vals,
            all_type_vals + extra_vals
        )

    def append_full(self):
        self.out.append("All", self.get_values())

    def append_generations(self):
        for gen in range(1, CURRENT_GENERATION + 1):
            generation_col = self.col(DokuFields.GENERATION).with_string(str(gen)).build()
            self.out.append(f"Gen {gen}", self.get_values(generation_col.condition))

    def append_regions(self):
        for region in REGIONS:
            region_col = self.col(DokuFields.REGION).with_string(region).build()
            self.out.append(region, self.get_values(region_col.condition))

    def append_mono_regions(self):
        for region in REGIONS:
            region_col = self.col(DokuFields.REGION).with_string(region).build()
            self.out.append(region + " Mono", self.get_values(region_col.condition, self.mono_col.condition))

    def append_types(self):
        def get_dual_type_progress(primary_type: str, secondary_type: str) -> Progress:
            primary_col = self.col(DokuFields.TYPE1).with_string(primary_type).build()
            secondary_col = self.col(DokuFields.TYPE2).with_string(secondary_type).build()
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

            extra_vals = [
                self.get_type_progress(poke_type, extra_col.condition)
                for extra_col in self.extra_cols
            ]

            values = get_values_from_progress(
                caught_vals, missing_vals, shiny_vals,
                mono_vals, dual_vals,
                all_type_vals + extra_vals
            )
            self.out.append(poke_type, values)

    def append_special(self):
        def append_category(title: str, column: Column):
            self.out.append(title, self.get_values(column.condition))

        append_category("Mono-Type", self.mono_col)
        append_category("Dual-Type", self.dual_col)
        self.out.blank_row()

        for evo_type in EvolutionType:
            append_category(evo_type, self.evo_cols[evo_type])
        self.out.blank_row()

        append_category("Partner", self.partner_col)
        append_category("Legendary", self.legend_col)
        append_category("Mythical", self.mythic_col)
        append_category("Baby", self.baby_col)
        append_category("Fossil", self.fossil_col)
        append_category("Paradox", self.paradox_col)
        append_category("Ultra Beast", self.ultra_col)
        append_category("Has Branch", self.branch_col)


def get_values_from_progress(
        caught_vals: Progress,
        missing_vals: Progress,
        shiny_vals: Progress,
        mono_vals: Progress,
        dual_vals: Progress,
        category_vals: List[Progress],
) -> List[str]:
    return [
        caught_vals.concatenated, shiny_vals.count,
        missing_vals.count, mono_vals.concatenated, dual_vals.concatenated,
        caught_vals.percent, shiny_vals.percent, mono_vals.reverse_percent, dual_vals.reverse_percent,
        *[vals.concatenated for vals in category_vals]
    ]


def write_doku_stats(doku: Doku):
    stats = DokuStats(doku)

    stats.append_full()
    stats.out.blank_row()

    stats.append_generations()
    stats.out.blank_row()

    stats.append_regions()
    stats.out.blank_row()

    stats.append_mono_regions()
    stats.out.blank_row()

    stats.append_types()
    stats.out.blank_row()

    stats.append_special()

    to_tsv(DOKU_STATS_OUTFILE, stats.out.rows)


def write_stats(dex: Dex, doku: Doku):
    write_dex_stats(dex)
    write_doku_stats(doku)
