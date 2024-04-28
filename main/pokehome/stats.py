from typing import List, Optional

from main.pokehome.constants.io import STATS_OUTFILE
from main.pokehome.constants.pokes import REGIONS
from main.pokehome.constants.sheets import DexFields, HiddenAbilityProgress, DEX_TAB, DexClassification
from main.pokehome.dex import Dex
from main.util.file_io import to_tsv
from main.util.sheets_formulas import caught_total_progress, count_with_percentage, condition_as_count, column_range


def get_stats(dex: Dex):
    class Column:
        def __init__(self, field: DexFields):
            self.start_index = 2
            self.col_range = column_range(dex.sheet.column(field), self.start_index, tab=DEX_TAB)

        def _with_value(self, value: str) -> "Column":
            self.value = value
            self.condition = f"{self.col_range}, {self.value}"
            return self

        def with_string(self, value: str) -> "Column":
            return self._with_value(f'"{value}"')

        def with_checkbox(self) -> "Column":
            return self._with_value("TRUE")

        def progress(self, condition: Optional[str]) -> str:
            return condition_as_count(self.condition, condition)

        def caught_total_progress(self, condition: Optional[str]) -> List[str]:
            return caught_total_progress(self.condition, condition)

    caught_col = Column(DexFields.CAUGHT_PROGRESS).with_checkbox()
    hidden_col = Column(DexFields.HIDDEN_PROGRESS).with_string("<>" + HiddenAbilityProgress.UNOBTAINED)
    nickname_col = Column(DexFields.NICKNAME).with_string("<>")
    shiny_col = Column(DexFields.SHINY).with_checkbox()

    class OutStats:
        def __init__(self):
            self.rows: List[List[str]] = []
            self.column_index = 0
            self.index = 0

        def new_column(self):
            self.column_index += 1
            self.index = 0

        def append(self, name: str, condition: Optional[str]):
            if self.index == len(self.rows):
                self.rows.append([""]*self.column_index*7)
            if self.column_index > 0:
                self.rows[self.index] += [""]

            have_values = caught_col.caught_total_progress(condition)
            hidden_value = hidden_col.progress(condition)
            nickname_value = nickname_col.progress(condition)
            shiny_value = shiny_col.progress(condition)

            self.rows[self.index] += [name, *have_values, hidden_value, nickname_value, shiny_value]
            self.index += 1

    out: OutStats = OutStats()
    out.append("All", None)

    class_col = Column(DexFields.CLASS)
    for classification in DexClassification:
        class_col.with_string(classification)
        out.append(classification, class_col.condition)
    out.new_column()

    box_col = Column(DexFields.BOX)
    for box in dex.boxes.boxes:
        box_col.with_string(box.name)
        out.append(box.name, box_col.condition)
    out.new_column()

    region_col = Column(DexFields.REGION)
    for region in REGIONS:
        region_col.with_string(region)
        out.append(region, region_col.condition)
    out.new_column()

    to_tsv(STATS_OUTFILE, out.rows)
