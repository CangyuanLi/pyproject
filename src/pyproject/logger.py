from __future__ import annotations

import enum
import sys
from typing import Callable, Optional

import rich.pretty
from rich.console import Console

from .spinner import Spinner


class Level(enum.Enum):
    ERROR = 1
    WARNING = 2
    INFO = 3

    def __lt__(self, other: Level) -> bool:
        if isinstance(other, Level):
            return self.value < other.value

        return NotImplemented


class Logger:
    def __init__(self, logging_level: Level):
        self._console = Console()
        self._err_console = Console(stderr=True)
        self._level = logging_level

    def pprint(self, *args, **kwargs):
        rich.pretty.pprint(*args, **kwargs, console=self._console)

    def info(self, *args, **kwargs):
        if Level.INFO > self._level:
            return None

        self._console.print(*args, **kwargs)

    def warning(self, warning: str, **kwargs):
        if Level.WARNING > self._level:
            return None

        self._err_console.print(
            f"[bold yellow]Warning[/bold yellow]: [yellow]{warning}[/yellow]", **kwargs
        )

    def error(self, error_message: str, **kwargs):
        self._err_console.print(
            f"[bold red]Error[/bold red]: [red]{error_message}[/red]", **kwargs
        )
        sys.exit(1)

    def spinner(
        self,
        func: Callable,
        text: str,
        delay: float = 0.1,
        prefix: str = "    ",
        suffix: str = " ",
        clear: bool = True,
        min_show_duration: Optional[float] = 0.2,
    ):
        if Level.INFO > self._level:
            return func()

        with Spinner(
            self._console, text, delay, prefix, suffix, clear, min_show_duration
        ):
            return func()
