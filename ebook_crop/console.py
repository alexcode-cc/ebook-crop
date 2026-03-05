"""終端機輸出模組，提供彩色輸出、進度條與詳細/靜默模式"""

from __future__ import annotations

from contextlib import contextmanager
from enum import IntEnum

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn

QUIET = 0
NORMAL = 1
VERBOSE = 2


class Verbosity(IntEnum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


class AppConsole:
    """應用程式輸出控制台，支援詳細/靜默模式與彩色輸出"""

    def __init__(self, verbosity: int = NORMAL) -> None:
        self.verbosity = verbosity
        self._console = Console(stderr=False)
        self._err_console = Console(stderr=True)

    def info(self, msg: str) -> None:
        """一般資訊（NORMAL 及以上顯示）"""
        if self.verbosity >= NORMAL:
            self._console.print(msg)

    def verbose(self, msg: str) -> None:
        """詳細資訊（僅 VERBOSE 顯示）"""
        if self.verbosity >= VERBOSE:
            self._console.print(f"[dim]{msg}[/dim]")

    def warning(self, msg: str) -> None:
        """警告訊息（始終顯示至 stderr）"""
        self._err_console.print(f"[yellow]警告：{msg}[/yellow]")

    def error(self, msg: str) -> None:
        """錯誤訊息（始終顯示至 stderr）"""
        self._err_console.print(f"[red bold]錯誤：{msg}[/red bold]")

    def success(self, msg: str) -> None:
        """成功訊息（NORMAL 及以上顯示）"""
        if self.verbosity >= NORMAL:
            self._console.print(f"[green]{msg}[/green]")

    def safe_print(self, msg: str) -> None:
        """Unicode-safe 輸出（NORMAL 及以上顯示）"""
        if self.verbosity >= NORMAL:
            try:
                self._console.print(msg, highlight=False)
            except UnicodeEncodeError:
                self._console.print(
                    msg.encode("ascii", errors="replace").decode("ascii"),
                    highlight=False,
                )

    @contextmanager
    def progress(self, total: int, description: str = "處理中"):
        """批次處理進度條（QUIET 模式下不顯示）"""
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
    """進度條追蹤器"""

    def __init__(self, progress: Progress, task_id) -> None:
        self._progress = progress
        self._task_id = task_id

    def advance(self, amount: int = 1) -> None:
        self._progress.advance(self._task_id, amount)


class _NoOpProgress:
    """靜默模式下的空操作進度條"""

    def advance(self, amount: int = 1) -> None:
        pass
