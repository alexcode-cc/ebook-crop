"""Terminal output module with colored output, progress bar, and verbosity control"""

from __future__ import annotations

from contextlib import contextmanager
from enum import IntEnum

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn

from ebook_crop.i18n import t

QUIET = 0
NORMAL = 1
VERBOSE = 2


class Verbosity(IntEnum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


class AppConsole:
    """Application console with verbosity control and colored output"""

    def __init__(self, verbosity: int = NORMAL) -> None:
        self.verbosity = verbosity
        self._console = Console(stderr=False)
        self._err_console = Console(stderr=True)

    def info(self, msg: str) -> None:
        """Normal info (NORMAL and above)"""
        if self.verbosity >= NORMAL:
            self._console.print(msg)

    def verbose(self, msg: str) -> None:
        """Verbose info (VERBOSE only)"""
        if self.verbosity >= VERBOSE:
            self._console.print(f"[dim]{msg}[/dim]")

    def warning(self, msg: str) -> None:
        """Warning (always shown to stderr)"""
        prefix = t("warning_prefix")
        self._err_console.print(f"[yellow]{prefix}{msg}[/yellow]")

    def error(self, msg: str) -> None:
        """Error (always shown to stderr)"""
        prefix = t("error_prefix")
        self._err_console.print(f"[red bold]{prefix}{msg}[/red bold]")

    def success(self, msg: str) -> None:
        """Success (NORMAL and above)"""
        if self.verbosity >= NORMAL:
            self._console.print(f"[green]{msg}[/green]")

    def safe_print(self, msg: str) -> None:
        """Unicode-safe output (NORMAL and above)"""
        if self.verbosity >= NORMAL:
            try:
                self._console.print(msg, highlight=False)
            except UnicodeEncodeError:
                self._console.print(
                    msg.encode("ascii", errors="replace").decode("ascii"),
                    highlight=False,
                )

    @contextmanager
    def progress(self, total: int, description: str = "Processing"):
        """Batch processing progress bar (hidden in QUIET mode)"""
        if self.verbosity <= QUIET:
            yield _NoOpProgress()
            return

        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self._console,
        )
        with progress:
            task_id = progress.add_task(description, total=total)
            yield _ProgressTracker(progress, task_id)


class _ProgressTracker:
    """Progress bar tracker"""

    def __init__(self, progress: Progress, task_id) -> None:
        self._progress = progress
        self._task_id = task_id

    def advance(self, amount: int = 1) -> None:
        self._progress.advance(self._task_id, amount)


class _NoOpProgress:
    """No-op progress bar for quiet mode"""

    def advance(self, amount: int = 1) -> None:
        pass
