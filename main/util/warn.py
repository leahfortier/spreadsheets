from contextlib import ContextDecorator
from enum import Enum
from typing import Any, List, Iterable, Callable, Optional

from terminology import in_red, in_yellow, in_white

from util.general import has_prefix, generic_name, is_number


class WarnLevel(Enum):
    ASSERT = "d e d",
    SEVERE = "Bark! Bark!! Bark!!!",
    WARN = "Woof! Woof!! Woof!!!",
    INFO = "Grrrr...",


def warn_if(c: bool, message: str):
    if c:
        print("DEPRECATED:", message)


def warn(message: str, level: WarnLevel = WarnLevel.WARN):
    match level:
        case WarnLevel.INFO:
            print(in_white(message).in_bold())
        case WarnLevel.WARN:
            print(in_yellow(message).in_bold())
        case WarnLevel.SEVERE:
            print(in_red(message).in_bold())
        case WarnLevel.ASSERT:
            assert False, message
        case _:
            assert False, f"{message}, Unknown level {level}"


class GuardDog:
    def __init__(self, message: str = None, level: WarnLevel = WarnLevel.WARN, beta_pup: bool = False):
        self.level = level
        self.messages = []
        if message:
            self.messages.append(message)

        if beta_pup:
            self.info = None
            self.woof = None
            self.bark = None
            self.kill = None
        else:
            self.info = GuardDog(level=WarnLevel.INFO, beta_pup=True)
            self.woof = GuardDog(level=WarnLevel.WARN, beta_pup=True)
            self.bark = GuardDog(level=WarnLevel.SEVERE, beta_pup=True)
            self.kill = GuardDog(level=WarnLevel.ASSERT, beta_pup=True)
            for guard in [self.info, self.woof, self.bark, self.kill]:
                guard.messages = self.messages

    def append_message(self, message: str):
        self.kill.nonempty(message)
        self.messages.append(message)

    def pop_message(self, expected: str = None) -> str:
        popped = self.messages.pop()
        if expected:
            self.eq(popped, expected)
        return popped

    def _message(self, *messages: str):
        all_messages = self.messages + [message for message in messages if message]
        if len(all_messages) == 0:
            return self.level.value
        base_message = all_messages.pop(0)
        remaining = ", ".join(all_messages)
        if remaining:
            return f'{base_message}: {remaining}'
        return base_message

    def _handle(self, expect_true: bool, *messages: str) -> bool:
        if expect_true:
            return True

        message = self._message(*messages)
        warn(message, self.level)
        return False

    def sniff(self, expect_true: bool, message: str = None) -> bool:
        return self._handle(expect_true, message)

    def prefix(self, value: str, prefixes: List[str], message: str = None) -> bool:
        return self._handle(has_prefix(value, *prefixes), message, f'{value} has no prefix in {prefixes}')

    def truthy(self, value: Any, message: str = None) -> bool:
        return self._handle(value, message, f"Unexpected falsy: {value}")

    def falsy(self, value: Any, message: str = None) -> bool:
        return self._handle(not value, message, f"Unexpected truthy: {value}")

    def info_if(self, info_if: bool, message: str = None) -> bool:
        return self.info.sniff(not info_if, message)

    def woof_if(self, woof_if: bool, message: str = None) -> bool:
        return self.woof.sniff(not woof_if, message)

    def bark_if(self, bark_if: bool, message: str = None) -> bool:
        return self.bark.sniff(not bark_if, message)

    def eq(self, first: Any, second: Any, message: str = None) -> bool:
        return self._handle(first == second, message, f'{first} != {second}')

    def uneq(self, first: Any, second: Any, message: str = None) -> bool:
        return self._handle(first != second, message, f'{first} == {second}')

    def greater(self, smaller: Any, larger: Any, message: str = None) -> bool:
        return self._handle(smaller < larger, message, f'{smaller} >= {larger}')

    def positive(self, positive: Any, message: str = None) -> bool:
        return self.greater(0, positive, message)

    def range(self, value: Any, min_value: Any, max_value: Any, message: str = None) -> bool:
        return self._handle(min_value <= value <= max_value, message, f'!({min_value} <= {value} <= {max_value})')

    def inside(self, value: Any, values: Iterable[Any], message: str = None) -> bool:
        return self._handle(value in values, message, f'{value} not in {values}')

    def nonside(self, value: Any, values: Iterable[Any], message: str = None) -> bool:
        return self._handle(value not in values, message, f'{value} in {values}')

    def none(self, value: Any, message: str = None) -> bool:
        message = f'{message}, {value}' if message else f'{value} is not None'
        return self._handle(value is None, message)

    def empty(self, value: Any, message: str = None) -> bool:
        return self._handle(not bool(value), message, f'{value} is non-empty')

    def nonempty(self, value: Any, message: str = None) -> bool:
        return self._handle(bool(value), message, f'{value} is empty')

    def len(self, first: List[Any], second: list[Any], message: str = None) -> bool:
        return self._handle(len(first) == len(second), message, f'Unequal Lengths: {len(first)} != {len(second)}')

    def close_enough(self, first: str, second: str, replace_chars="\"", message: str = None) -> bool:
        return self._handle(
            generic_name(first, replace_chars) == generic_name(second, replace_chars),
            message, f"\n\t{first}\n\t{second}"
        )

    def empty_or_eq(self, possible_empty: Any, non_empty: Any, message: str = None) -> bool:
        self.nonempty(non_empty, message)
        if possible_empty:
            return self.eq(possible_empty, non_empty, message)
        # I know this looks dumb but I haven't worked in this code in a bit
        # and I just want to make sure the return value is consistent
        return self.truthy(True, message)

    def number(self, number_string: str, message: str = None) -> bool:
        return self._handle(is_number(number_string), message, f'Not a number: {number_string}')



# Automatically pops any appended messages on exit
class message_guardian(ContextDecorator):
    def __init__(self, guard: GuardDog, name: str = None):
        self.guard = guard
        self.name = name

        self.enter_count: int
        self.added: List[str]
        self.original_append: Callable[[str], None]
        self.original_pop: Callable[[Optional[str]], str]

    def __call__(self, func):
        if not self.name:
            self.name = func.__name__
        return super().__call__(func)

    def guardian_append(self, message: str):
        self.original_append(message)
        self.added.append(message)

    def guardian_pop(self, expected: str = None) -> str:
        popped = self.original_pop(expected)
        unadded = self.added.pop()
        self.guard.kill.eq(unadded, popped)
        return popped

    def __enter__(self):
        self.enter_count = len(self.guard.messages)
        self.added = []

        self.original_append = self.guard.append_message
        self.original_pop = self.guard.pop_message

        self.guard.append_message = self.guardian_append
        self.guard.pop_message = self.guardian_pop

        self.guardian_append(self.name)

    def __exit__(self, exc_type, exc_value, traceback):
        while len(self.added) > 0:
            self.guardian_pop()
        self.guard.kill.eq(len(self.guard.messages), self.enter_count)

        self.guard.append_message = self.original_append
        self.guard.pop_message = self.original_pop
