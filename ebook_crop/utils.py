"""共用工具函式"""

from __future__ import annotations

import shutil
from pathlib import Path


def _safe_print(msg: str) -> None:
    """輸出至 stdout，遇編碼錯誤時改用 ASCII 替代字元"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def save_config_to_output(config_path: Path, output_pdf_path: Path) -> None:
    """
    將使用的 config.toml 複製到輸出目錄，檔名為處理文件的檔名。

    Args:
        config_path: 設定檔路徑
        output_pdf_path: 輸出 PDF 路徑（用於決定檔名與目錄）
    """
    output_dir = output_pdf_path.parent
    config_copy_name = f"{output_pdf_path.stem}.toml"
    config_copy_path = output_dir / config_copy_name
    shutil.copy2(config_path, config_copy_path)
