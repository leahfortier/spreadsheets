import re

SECOND_MILLIS = 1000
MINUTE_MILLIS = 60 * SECOND_MILLIS
HOUR_MILLIS = 60 * MINUTE_MILLIS


time_format = "(?:([0-9]+):)?([0-9]{1,2}):([0-9]{2})[. ]([0-9]{3})"


def string_to_millis(time: str) -> int:
    if not re.fullmatch(time_format, time):
        print("No match", time)
        return 0
    match = re.compile(time_format).match(time)
    hours: int = int(match.group(1) or 0)
    minutes: int = int(match.group(2))
    seconds: int = int(match.group(3))
    millis: int = int(match.group(4))
    return millis + seconds * SECOND_MILLIS + minutes * MINUTE_MILLIS + hours * HOUR_MILLIS


def millis_to_string(millis: int) -> str:
    hours = millis // HOUR_MILLIS
    millis -= hours * HOUR_MILLIS
    minutes = millis // MINUTE_MILLIS
    millis -= minutes * MINUTE_MILLIS
    seconds = millis // SECOND_MILLIS
    millis -= seconds * SECOND_MILLIS
    hours_minutes = f'{minutes}' if hours == 0 else f'{hours}:{minutes:02}'
    return f'{hours_minutes}:{seconds:02}.{millis:03}'
