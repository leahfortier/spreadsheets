from typing import List, Tuple, Self


class Progress:
    def __init__(self, raw_count: str, raw_total: str):
        self.raw_count = raw_count
        self.raw_total = raw_total
        self.count = f'={raw_count}'
        self.total = f'={raw_total}'
        self.concatenated = f'=CONCATENATE({raw_count}, "/", {raw_total})'

        raw_percent = f'({raw_count}) / ({raw_total})'
        zero_value = f'"--"'
        self.percent = if_zero(raw_total, zero_value, raw_percent)
        self.reverse_percent = if_zero(raw_total, zero_value, f'1 - {raw_percent}')

    def values(self) -> List[str]:
        return [self.count, self.total, self.percent]

    def with_or(self, progress: Self) -> Self:
        return Progress(
            f'{self.raw_count} + {progress.raw_count}',
            f'{self.raw_total} + {progress.raw_total}'
        )


def _raw_count_total(progress_condition: str, *required_conditions: str) -> Tuple[str, str]:
    if len(required_conditions) == 0:
        count = f'COUNTIF({progress_condition})'
        total = f'COUNTA({progress_condition[:progress_condition.index(",")]})'
    else:
        joined_conditions = ", ".join(required_conditions)
        count = f'COUNTIFS({progress_condition}, {joined_conditions})'
        total = f'COUNTIFS({joined_conditions})'
    return count, total


def get_progress(progress_condition: str, *required_conditions: str) -> Progress:
    count, total = _raw_count_total(progress_condition, *required_conditions)
    return Progress(count, total)


# Used when either first condition OR second condition can be true for progress
def or_progress(progress_condition: str, first_condition: str, second_condition: str) -> Progress:
    first = get_progress(progress_condition, first_condition)
    second = get_progress(progress_condition, second_condition)
    return first.with_or(second)


def progress_difference(first: Progress, second: Progress) -> Progress:
    count = f'{first.raw_count} - {second.raw_count}'
    total = f'{first.raw_total} - {second.raw_total}'
    return Progress(count, total)


def if_zero(is_zero: str, zero_value: str, nonzero_value: str) -> str:
    return f'=IF({is_zero}=0, {zero_value}, {nonzero_value})'


def if_image(condition: str, true_url: str, false_url: str) -> str:
    return f'=IF({condition}, IMAGE("{true_url}"), IMAGE("{false_url}"))'


def image(url: str) -> str:
    return f'=IMAGE("{url}")'


def column_range(column: str, start_index: int = 2, tab: str = "", fixed=False) -> str:
    tab_prefix = f"'{tab}'!" if tab else ""
    index = str(start_index)
    if fixed:
        index = "$" + index
    return f"{tab_prefix}{column}{index}:{column}"


def index_value(col_range: str, start_index: int = 2) -> str:
    return f'INDEX({col_range}, ROW() - {start_index - 1})'


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
