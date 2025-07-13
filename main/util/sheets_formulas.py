from typing import List, Optional, Tuple


class Progress:
    def __init__(self, raw_count: str, raw_total: str):
        self.count = f'={raw_count}'
        self.total = f'={raw_total}'
        self.percent = f'=({raw_count}) / ({raw_total})'
        self.concatenated = f'=CONCATENATE({raw_count}, "/", {raw_total})'

    def values(self) -> List[str]:
        return [self.count, self.total, self.percent]


def _raw_count_total(progress_condition: str, *required_conditions: str) -> Tuple[str, str]:
    if len(required_conditions) == 0:
        count = f'COUNTIF({progress_condition})'
        total = f'COUNTA({progress_condition[:progress_condition.index(",")]})'
    else:
        joined_conditions = ", ".join(required_conditions)
        count = f'COUNTIFS({progress_condition}, {joined_conditions})'
        total = f'COUNTIFS({joined_conditions})'
    return count, total


def caught_total_progress(progress_condition: str, *required_conditions: str) -> Progress:
    count, total = _raw_count_total(progress_condition, *required_conditions)
    return Progress(count, total)


# Used when either first condition OR second condition can be true for progress
def or_caught_total_progress(progress_condition: str, first_condition: str, second_condition: str) -> Progress:
    count1, total1 = _raw_count_total(progress_condition, first_condition)
    count2, total2 = _raw_count_total(progress_condition, second_condition)
    return Progress(
        f'{count1} + {count2}',
        f'{total1} + {total2}'
    )


def column_progress(col_range: str, col_value: str) -> str:
    return caught_total_progress(f'{col_range}, {col_value}', None).percent


def count_with_percentage(progress_condition: str, required_condition: Optional[str]) -> str:
    progress = caught_total_progress(progress_condition, required_condition)
    count = progress.count.lstrip('=')
    percentage = progress.percent.lstrip('=')
    return f'=JOIN("", {count}, " (", TO_PERCENT({percentage}), ")")'


def condition_as_count(progress_condition: str, *required_conditions: str) -> str:
    return caught_total_progress(progress_condition, *required_conditions).count


def column_range(column: str, start_index: int = 2, tab: str = "", fixed=False) -> str:
    tab_prefix = f"'{tab}'!" if tab else ""
    index = str(start_index)
    if fixed:
        index = "$" + index
    return f"{tab_prefix}{column}{index}:{column}"


def column_name(col_index: int) -> str:
    length = 1
    current = 26
    value = col_index
    while value >= current:
        value -= current
        current *= 26
        length += 1

    answer = ""
    for i in range(0, length):
        mod = value % 26
        answer = chr(mod + ord('A')) + answer
        value //= 26

    return answer
