from typing import List, Optional


def caught_total_progress(progress_condition: str, required_condition: str = None) -> List[str]:
    if not required_condition:
        count = f'COUNTIF({progress_condition})'
        total = f'COUNTA({progress_condition[:progress_condition.index(",")]})'
    else:
        count = f'COUNTIFS({progress_condition}, {required_condition})'
        total = f'COUNTIF({required_condition})'
    return [
        f'={count}',
        f'={total}',
        f'={count} / {total}',
    ]


def column_progress(col_range: str, col_value: str) -> str:
    return caught_total_progress(f'{col_range}, {col_value}', None)[2]


def count_with_percentage(progress_condition: str, required_condition: Optional[str]) -> str:
    progress = caught_total_progress(progress_condition, required_condition)
    count = progress[0].lstrip('=')
    percentage = progress[2].lstrip('=')
    return f'=JOIN("", {count}, " (", TO_PERCENT({percentage}), ")")'


def condition_as_count(progress_condition: str, required_condition: Optional[str]) -> str:
    return caught_total_progress(progress_condition, required_condition)[0]


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
