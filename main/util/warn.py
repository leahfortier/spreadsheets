from contextlib import ContextDecorator
from enum import Enum
from typing import Any, List, Iterable, Callable, Optional

from terminology import in_red


def warn(message: str):
    print(in_red(message).in_bold())


def warn_if(condition: bool, message: str):
    if condition:
        warn(message)


class WarnLevel(Enum):
    ASSERT = "Bark! Bark!! Bark!!!",
    WARN = "Woof! Woof!! Woof!!!",
    INFO = "Grrrr...",


class GuardDog:
    def __init__(self, message: str = None, level: WarnLevel = WarnLevel.WARN):
        self.level = level
        self.messages = []
        if message:
            self.messages.append(message)

    def append_message(self, message: str):
        self.nonempty(message, level=WarnLevel.ASSERT)
        self.messages.append(message)

    def pop_message(self, expected: str = None) -> str:
        popped = self.messages.pop()
        if expected:
            self.eq(popped, expected)
        return popped

    def _message(self, level: WarnLevel, *messages: str):
        all_messages = self.messages + [message for message in messages if message]
        if len(all_messages) == 0:
            return level.value
        base_message = all_messages.pop(0)
        remaining = ", ".join(all_messages)
        if remaining:
            return f'{base_message}: {remaining}'
        return base_message

    def _handle(self, expect_true: bool, level: WarnLevel = None, *messages: str):
        if expect_true:
            return

        level = level or self.level
        message = self._message(level, *messages)
        match level:
            case WarnLevel.INFO:
                print(message)
            case WarnLevel.WARN:
                warn(message)
            case WarnLevel.ASSERT:
                assert False, message
            case _:
                assert False, f"{message}, Unknown level {level}, Default: {self.level}"

    def woof_if(self, woof_if: bool, message: str = None):
        self._handle(not woof_if, WarnLevel.WARN, message)

    def bark_if(self, bark_if: bool, message: str = None):
        self._handle(not bark_if, WarnLevel.ASSERT, message)

    def sniff(self, expect_true: bool, message: str = None, level: WarnLevel = None):
        self._handle(expect_true, level, message)

    def eq(self, first: Any, second: Any, message: str = None, level: WarnLevel = None):
        self._handle(first == second, level, message, f'{first} != {second}')

    def uneq(self, first: Any, second: Any, message: str = None, level: WarnLevel = None):
        self._handle(first != second, level, message, f'{first} == {second}')

    def greater(self, smaller: Any, larger: Any, message: str = None, level: WarnLevel = None):
        self._handle(smaller < larger, level, message, f'{smaller} >= {larger}')

    def range(self, value: Any, min_value: Any, max_value: Any, message: str = None, level: WarnLevel = None):
        self._handle(min_value <= value <= max_value, level, message, f'!({min_value} <= {value} <= {max_value})')

    def inside(self, value: Any, values: Iterable[Any], message: str = None, level: WarnLevel = None):
        self._handle(value in values, level, message, f'{value} not in {values}')

    def none(self, value: Any, message: str = None, level: WarnLevel = None):
        self._handle(value is None, level, message, f'{value} is not None')

    def empty(self, value: Any, message: str = None, level: WarnLevel = None):
        self._handle(not bool(value), level, message, f'{value} is non-empty')

    def nonempty(self, value: Any, message: str = None, level: WarnLevel = None):
        self._handle(bool(value), level, message, f'{value} is empty')


# Automatically pops any appended messages on exit
class message_guardian(ContextDecorator):
    def __init__(self, guard: GuardDog):
        self.guard = guard

        self.name: str

        self.enter_count: int
        self.added: List[str]
        self.original_append: Callable[[str], None]
        self.original_pop: Callable[[Optional[str]], str]

    def __call__(self, func):
        self.name = func.__name__
        return super().__call__(func)

    def guardian_append(self, message: str):
        self.original_append(message)
        self.added.append(message)

    def guardian_pop(self, expected: str = None) -> str:
        popped = self.original_pop(expected)
        unadded = self.added.pop()
        self.guard.eq(unadded, popped, level=WarnLevel.ASSERT)
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
        self.guard.eq(len(self.guard.messages), self.enter_count, level=WarnLevel.ASSERT)

        self.guard.append_message = self.original_append
        self.guard.pop_message = self.original_pop
