import itertools
import sys
import threading
import time
from typing import Optional

from rich.console import Console

BACKSPACE = "\b"
CLEAR_LINE = "\033[K"
CHECKMARK = "[green]\u2713[/green]"
XMARK = "[red]\u2717[/red]"


class Spinner:
    def __init__(
        self,
        console: Console,
        text: str,
        delay: float = 0.1,
        prefix: str = "",
        suffix: str = "",
        clear: bool = False,
        min_show_duration: Optional[float] = None,
    ):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        self.clear = clear
        self.console = console
        self.min_show_duration = min_show_duration

        self._start_time = time.perf_counter()

        console.print(f"{prefix}{text}{suffix}", end="")

    def clear_line(self):
        sys.stdout.write("\r")
        sys.stdout.write(CLEAR_LINE)

    def write_next(self):
        with self._screen_lock:
            if not self.spinner_visible:
                self.console.print(next(self.spinner), end="")
                self.spinner_visible = True
                sys.stdout.flush()

    def remove_spinner(self, end_mark: str = "", cleanup: bool = False) -> None:
        with self._screen_lock:
            if not self.spinner_visible:
                return None

            sys.stdout.write(BACKSPACE)
            self.spinner_visible = False
            if cleanup:
                self.console.print(end_mark, end="")

                if self.min_show_duration is not None:
                    sleep_time = self.min_show_duration - (
                        time.perf_counter() - self._start_time
                    )

                    if sleep_time > 0:
                        time.sleep(sleep_time)

                if self.clear:
                    self.clear_line()
                else:
                    sys.stdout.write("\n")

            sys.stdout.flush()

    def spinner_task(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    def __enter__(self):
        if sys.stdout.isatty():  # if file stream is active
            self._screen_lock = threading.Lock()
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task)
            self.thread.start()

    def __exit__(
        self, exception_type: Optional[BaseException], exception_value, traceback
    ):
        end_mark = CHECKMARK

        if exception_type is not None:
            end_mark = XMARK

        if sys.stdout.isatty():
            self.busy = False
            self.remove_spinner(end_mark, cleanup=True)
        else:
            sys.stdout.write("\r")

        if exception_type is not None:
            raise exception_value
