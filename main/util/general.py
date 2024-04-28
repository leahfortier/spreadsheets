from typing import List

titlecase_exceptions: List[str] = ["a", "and", "an", "of", "or", "the"]


def title(s: str) -> str:
    s = s.title().strip()
    for exception in titlecase_exceptions:
        s = s.replace(f" {exception.capitalize()} ", f" {exception.lower()} ")
    return s


def has_prefix(s: str, prefixes: List[str]) -> bool:
    for prefix in prefixes:
        if s.startswith(prefix):
            return True
    return False


def remove_prefix(s: str, prefixes: List[str]) -> str:
    for prefix in prefixes:
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s


def remove_suffix(s: str, suffixes: List[str]) -> str:
    for suffix in suffixes:
        if s.endswith(suffix):
            s = s[:-(len(suffix))]
    return s


def is_empty(row: List[str]) -> bool:
    for val in row:
        if val != '':
            return False
    return True


def generic_name(styled_name: str) -> str:
    name = styled_name.lower().replace("\"", "")
    return name
