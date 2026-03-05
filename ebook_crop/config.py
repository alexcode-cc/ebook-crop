"""設定檔載入與解析"""

from __future__ import annotations

import sys
from pathlib import Path

import tomli


def load_config(config_path: Path) -> dict:
    """載入 config.toml 設定檔"""
    if not config_path.exists():
        print(f"錯誤：找不到設定檔 {config_path}", file=sys.stderr)
        sample = config_path.parent / "config-sample.toml"
        if sample.exists():
            print(f"提示：可複製 {sample} 為 {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomli.load(f)


def format_rotation_display(rotation_list: list[dict]) -> str:
    """將 rotation 設定格式化為顯示字串，含頁次與角度。"""
    parts: list[str] = []
    for r in rotation_list:
        angle = float(r.get("angle", 0))
        angle_str = f"{angle:g}°"

        if "pages" in r:
            val = r["pages"]
            skip = int(r.get("skip", 0))
            if isinstance(val, str):
                val = val.strip()
                if "-" in val and "," not in val:
                    parts_range = val.split("-", 1)
                    start_raw, end_raw = parts_range[0].strip(), parts_range[1].strip()
                    if end_raw == "0":
                        pages_str = f"第 {start_raw if start_raw != '0' else '1'} 頁至最後一頁"
                    else:
                        pages_str = f"第 {val} 頁"
                    if skip > 0:
                        pages_str += f"（每隔{skip}頁）"
                else:
                    pages_str = f"第 {val} 頁"
            elif isinstance(val, (list, tuple)):
                pages_str = f"第 {','.join(str(x) for x in val)} 頁"
            else:
                pages_str = f"第 {val} 頁"
        elif "page" in r:
            p = int(r["page"])
            pages_str = f"第 {p} 頁"
        else:
            continue

        parts.append(f"{pages_str} {angle_str}")
    return "；".join(parts)


def parse_rotation_list(
    rotation_list: list[dict],
    total_pages: int = 0,
) -> dict[int, float]:
    """
    解析 [[rotation]] 設定，支援：
    - page：單頁
    - pages：多頁，可為 "1,3,5"、"3-9" 或 "3-0"（0=最後一頁）、"0-0"（全文件）
    - skip：搭配範圍使用，每隔 N 頁取一頁
    回傳 {page_index: angle}，0-based，已排序。
    """
    rotation_map: dict[int, float] = {}
    for r in rotation_list:
        a = float(r.get("angle", 0))
        skip = int(r.get("skip", 0))
        if skip < 0:
            skip = 0
        pages: list[int] = []

        if "pages" in r:
            val = r["pages"]
            if isinstance(val, int):
                if val > 0:
                    pages = [val]
            elif isinstance(val, str):
                val = val.strip()
                if "-" in val and "," not in val:
                    # 範圍格式：3-9 或 3-0（0=最後一頁）、0-0（全文件）
                    parts = val.split("-", 1)
                    if len(parts) == 2:
                        start_raw = parts[0].strip()
                        end_raw = parts[1].strip()
                        start = 1 if start_raw == "0" else int(start_raw)
                        end = total_pages if end_raw == "0" and total_pages > 0 else int(end_raw)
                        if end_raw == "0" and total_pages <= 0:
                            continue  # 無法解析「至最後一頁」，跳過此區塊
                        if start <= end and end > 0:
                            range_pages = list(range(start, end + 1))
                            step = skip + 1
                            pages = [range_pages[i] for i in range(0, len(range_pages), step)]
                else:
                    # 逗號分隔：1,3,5,7
                    pages = [int(x.strip()) for x in val.split(",") if x.strip()]
            elif isinstance(val, (list, tuple)):
                pages = [int(x) for x in val]

        if "page" in r:
            p = int(r["page"])
            if p > 0:
                pages.append(p)

        for p in pages:
            if p > 0:
                rotation_map[p - 1] = a  # 1-based -> 0-based

    return dict(sorted(rotation_map.items()))
