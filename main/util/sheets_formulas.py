from typing import List, Optional, Tuple


def _raw_count_total(progress_condition: str, *required_conditions: str) -> Tuple[str, str]:
    if len(required_conditions) == 0:
        count = f'COUNTIF({progress_condition})'
        total = f'COUNTA({progress_condition[:progress_condition.index(",")]})'
    else:
        joined_conditions = ", ".join(required_conditions)
        count = f'COUNTIFS({progress_condition}, {joined_conditions})'
        total = f'COUNTIFS({joined_conditions})'
    return count, total


def caught_total_progress(progress_condition: str, *required_conditions: str) -> List[str]:
    count, total = _raw_count_total(progress_condition, *required_conditions)
    return [
        f'={count}',
        f'={total}',
        f'={count} / {total}',
    ]


# Used when either first condition OR second condition can be true for progress
def or_caught_total_progress(progress_condition: str, first_condition: str, second_condition: str) -> List[str]:
    count1, total1 = _raw_count_total(progress_condition, first_condition)
    count2, total2 = _raw_count_total(progress_condition, second_condition)
    return [
        f'={count1} + {count2}',
        f'={total1} + {total2}',
        f'=({count1} + {count2}) / ({total1} + {total2})',
    ]


def column_progress(col_range: str, col_value: str) -> str:
    return caught_total_progress(f'{col_range}, {col_value}', None)[2]


def count_with_percentage(progress_condition: str, required_condition: Optional[str]) -> str:
    progress = caught_total_progress(progress_condition, required_condition)
    count = progress[0].lstrip('=')
    percentage = progress[2].lstrip('=')
    return f'=JOIN("", {count}, " (", TO_PERCENT({percentage}), ")")'


def condition_as_count(progress_condition: str, *required_conditions: str) -> str:
    return caught_total_progress(progress_condition, *required_conditions)[0]


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
