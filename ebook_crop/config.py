"""設定檔載入、解析與驗證"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import tomli

# 單位轉換因子（轉為 PDF 點）
_UNIT_FACTORS: dict[str, float] = {
    "pt": 1.0,
    "cm": 72.0 / 2.54,
    "mm": 72.0 / 25.4,
    "in": 72.0,
    "inch": 72.0,
}

_UNIT_PATTERN = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?)\s*(pt|cm|mm|inch|in)?\s*$",
    re.IGNORECASE,
)


def convert_margin_value(value: int | float | str, key: str = "") -> float:
    """
    將留白值轉換為 PDF 點。

    支援格式：
    - 數字：直接作為點（向後相容）
    - 字串："36"、"1cm"、"10mm"、"0.5in"、"0.5inch"、"36pt"
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        label = f" ({key})" if key else ""
        raise ValueError(f"無效的留白值{label}：{value!r}，需為數字或含單位的字串")

    match = _UNIT_PATTERN.match(value)
    if not match:
        label = f" ({key})" if key else ""
        raise ValueError(
            f"無效的留白值{label}：{value!r}，"
            f"支援格式：36、1cm、10mm、0.5in、0.5inch、36pt"
        )

    num = float(match.group(1))
    unit = (match.group(2) or "pt").lower()
    return num * _UNIT_FACTORS[unit]


def _convert_margins(margins: dict) -> dict[str, float]:
    """轉換 margins 區段中所有值的單位"""
    converted = {}
    for key in ("left", "right", "top", "bottom"):
        raw = margins.get(key, 0)
        converted[key] = convert_margin_value(raw, key)
    return converted


def validate_config(cfg: dict) -> list[str]:
    """
    驗證設定檔，回傳錯誤訊息列表（空表示無錯誤）。

    驗證項目：
    - margins 各值為非負數或有效單位字串
    - pages.start 為非負整數
    - pages.end 為 0 或 -1
    - rotation 各筆含有效 page/pages 與 angle
    """
    errors: list[str] = []

    # 驗證 margins
    margins = cfg.get("margins", {})
    for key in ("left", "right", "top", "bottom"):
        raw = margins.get(key, 0)
        try:
            val = convert_margin_value(raw, key)
            if val < 0:
                errors.append(f"[margins] {key} 不可為負值：{val}")
        except ValueError as e:
            errors.append(str(e))

    # 驗證 pages
    pages = cfg.get("pages", {})
    start = pages.get("start", 2)
    if not isinstance(start, (int, float)) or int(start) < 0:
        errors.append(f"[pages] start 需為非負整數，目前為：{start!r}")

    end = pages.get("end", 0)
    if not isinstance(end, (int, float)) or int(end) not in (0, -1):
        errors.append(f"[pages] end 需為 0（至最後一頁）或 -1（不含最後一頁），目前為：{end!r}")

    # 驗證 rotation
    rotation_list = cfg.get("rotation", [])
    if not isinstance(rotation_list, list):
        errors.append(f"[[rotation]] 需為陣列，目前為：{type(rotation_list).__name__}")
    else:
        for idx, r in enumerate(rotation_list):
            if not isinstance(r, dict):
                errors.append(f"[[rotation]] 第 {idx + 1} 筆需為表格，目前為：{type(r).__name__}")
                continue

            if "page" not in r and "pages" not in r:
                errors.append(f"[[rotation]] 第 {idx + 1} 筆缺少 page 或 pages 欄位")

            angle = r.get("angle")
            if angle is None:
                errors.append(f"[[rotation]] 第 {idx + 1} 筆缺少 angle 欄位")
            elif not isinstance(angle, (int, float)):
                errors.append(f"[[rotation]] 第 {idx + 1} 筆 angle 需為數字，目前為：{angle!r}")

    return errors


def load_config(config_path: Path) -> dict:
    """載入 config.toml 設定檔，含驗證與單位轉換"""
    if not config_path.exists():
        print(f"錯誤：找不到設定檔 {config_path}", file=sys.stderr)
        sample = config_path.parent / "config-sample.toml"
        if sample.exists():
            print(f"提示：可複製 {sample} 為 {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        cfg = tomli.load(f)

    # 驗證設定
    errors = validate_config(cfg)
    if errors:
        print("錯誤：設定檔驗證失敗：", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # 轉換留白單位
    if "margins" in cfg:
        cfg["margins"] = _convert_margins(cfg["margins"])

    return cfg


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


def format_margins_display(margins: dict[str, float]) -> str:
    """格式化留白設定為顯示字串，含點與公分對照"""
    def _fmt(val: float) -> str:
        cm = val / (72.0 / 2.54)
        return f"{val:.1f}pt ({cm:.2f}cm)"

    return (
        f"左 {_fmt(margins.get('left', 0))}, "
        f"右 {_fmt(margins.get('right', 0))}, "
        f"上 {_fmt(margins.get('top', 0))}, "
        f"下 {_fmt(margins.get('bottom', 0))}"
    )


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
