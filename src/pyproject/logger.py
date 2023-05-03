from __future__ import annotations
import enum
from typing import Callable, Optional

from rich.console import Console
import rich.pretty
from .spinner import Spinner


class Level(enum.Enum):
    ERROR = 1
    INFO = 2

    def __lt__(self, other: Level) -> bool:
        if isinstance(other, Level):
            return self.value < other.value

        return NotImplemented


class CustomConsole(Console):
    def __init__(self, logging_level: Level):
        super().__init__()
        self._level = logging_level

    def pprint(self, *args, **kwargs):
        rich.pretty.pprint(*args, **kwargs, console=self)

    def info(self, *args, **kwargs):
        if Level.INFO > self._level:
            return None

        self.print(*args, **kwargs)

    def error(self, error_message: str, **kwargs):
        self.print(f"[bold red]Error[/bold red]: [red]{error_message}[/red]", **kwargs)

    def spinner(
        self,
        func: Callable,
        text: str,
        delay: float = 0.1,
        prefix: str = "    ",
        suffix: str = " ",
        clear: bool = False,
        min_show_duration: Optional[float] = None,
    ):
        if Level.INFO > self._level:
            return func()

        with Spinner(self, text, delay, prefix, suffix, clear, min_show_duration):
            return func()
