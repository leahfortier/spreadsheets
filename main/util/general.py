from enum import Enum
from typing import List, TypeVar

from terminology import in_red

FieldsEnum = TypeVar("FieldsEnum", bound=Enum)

titlecase_exceptions: List[str] = ["a", "and", "an", "of", "or", "the"]


def title(s: str) -> str:
    s = s.title().strip()
    for exception in titlecase_exceptions:
        s = s.replace(f" {exception.capitalize()} ", f" {exception.lower()} ")
    return s


def has_prefix(s: str, *prefixes: str) -> bool:
    for prefix in prefixes:
        if s.startswith(prefix):
            return True
    return False


def remove_prefix(s: str, *prefixes: str) -> str:
    for prefix in prefixes:
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s


def remove_suffix(s: str, *suffixes: str) -> str:
    for suffix in suffixes:
        if s.endswith(suffix):
            s = s[:-(len(suffix))]
    return s


def is_empty(row: List[str]) -> bool:
    for val in row:
        if val != '':
            return False
    return True


def all_unique(row: List[str], exceptions: List[str] = None) -> bool:
    exceptions = exceptions or []
    for i in range(0, len(row)):
        for j in range(i + 1, len(row)):
            if row[i] == row[j] and row[i] not in exceptions:
                return False
    return True


def generic_name(styled_name: str, replace_chars="\"") -> str:
    name = styled_name.lower()
    for char in replace_chars:
        name = name.replace(char, "")
    return name.strip()


def to_str(field: str | Enum) -> str:
    if isinstance(field, Enum):
        field = field.value
    return field


def flatten(lists: List[List[str]]) -> List[str]:
    return [value for sublist in lists for value in sublist]
