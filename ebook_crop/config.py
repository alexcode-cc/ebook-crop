"""Config file loading, parsing, and validation"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import tomli

from ebook_crop.i18n import t

# Unit conversion factors (to PDF points)
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
    """Convert margin value to PDF points."""
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        label = f" ({key})" if key else ""
        raise ValueError(t("err_invalid_margin", label=label, value=value))

    match = _UNIT_PATTERN.match(value)
    if not match:
        label = f" ({key})" if key else ""
        raise ValueError(t("err_invalid_margin_format", label=label, value=value))

    num = float(match.group(1))
    unit = (match.group(2) or "pt").lower()
    return num * _UNIT_FACTORS[unit]


def _convert_margins(margins: dict) -> dict[str, float]:
    """Convert all margin values in the margins section"""
    converted = {}
    for key in ("left", "right", "top", "bottom"):
        raw = margins.get(key, 0)
        converted[key] = convert_margin_value(raw, key)
    return converted


def validate_config(cfg: dict) -> list[str]:
    """Validate config, return list of error messages (empty = valid)."""
    errors: list[str] = []

    # Validate margins
    margins = cfg.get("margins", {})
    for key in ("left", "right", "top", "bottom"):
        raw = margins.get(key, 0)
        try:
            val = convert_margin_value(raw, key)
            if val < 0:
                errors.append(t("err_margin_negative", key=key, val=val))
        except ValueError as e:
            errors.append(str(e))

    # Validate pages
    pages = cfg.get("pages", {})
    start = pages.get("start", 2)
    if not isinstance(start, (int, float)) or int(start) < 0:
        errors.append(t("err_pages_start", val=start))

    end = pages.get("end", 0)
    if not isinstance(end, (int, float)) or int(end) not in (0, -1):
        errors.append(t("err_pages_end", val=end))

    # Validate rotation
    rotation_list = cfg.get("rotation", [])
    if not isinstance(rotation_list, list):
        errors.append(t("err_rotation_not_array", type=type(rotation_list).__name__))
    else:
        for idx, r in enumerate(rotation_list):
            if not isinstance(r, dict):
                errors.append(t("err_rotation_not_table", idx=idx + 1,
                                type=type(r).__name__))
                continue

            if "page" not in r and "pages" not in r:
                errors.append(t("err_rotation_no_page", idx=idx + 1))

            angle = r.get("angle")
            if angle is None:
                errors.append(t("err_rotation_no_angle", idx=idx + 1))
            elif not isinstance(angle, (int, float)):
                errors.append(t("err_rotation_bad_angle", idx=idx + 1, val=angle))

    return errors


def load_config(config_path: Path) -> dict:
    """Load config.toml with validation and unit conversion"""
    if not config_path.exists():
        print(t("err_config_not_found", path=config_path), file=sys.stderr)
        sample = config_path.parent / "config-sample.toml"
        if sample.exists():
            print(t("hint_copy_sample", sample=sample, config=config_path), file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        cfg = tomli.load(f)

    # Validate
    errors = validate_config(cfg)
    if errors:
        print(t("err_config_validation"), file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Convert margin units
    if "margins" in cfg:
        cfg["margins"] = _convert_margins(cfg["margins"])

    # Process auto-detect margins
    if "auto_margins" in cfg:
        am = cfg["auto_margins"]
        if am.get("enabled", False):
            offsets = {}
            for key in ("left", "right", "top", "bottom"):
                raw = am.get(key, 0)
                offsets[key] = convert_margin_value(raw, f"auto_margins.{key}")
            cfg["_auto_margins"] = {"offsets": offsets}

    return cfg


def format_rotation_display(rotation_list: list[dict]) -> str:
    """Format rotation config for display."""
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
                        s = start_raw if start_raw != "0" else "1"
                        pages_str = t("page_range_to_last", start=s)
                    else:
                        pages_str = t("page_n", val=val)
                    if skip > 0:
                        pages_str += t("every_n_pages", skip=skip)
                else:
                    pages_str = t("page_n", val=val)
            elif isinstance(val, (list, tuple)):
                pages_str = t("page_n", val=",".join(str(x) for x in val))
            else:
                pages_str = t("page_n", val=val)
        elif "page" in r:
            p = int(r["page"])
            pages_str = t("page_n", val=p)
        else:
            continue

        parts.append(f"{pages_str} {angle_str}")
    return "; ".join(parts)


def format_margins_display(margins: dict[str, float]) -> str:
    """Format margins for display with pt and cm values"""
    def _fmt(val: float) -> str:
        cm = val / (72.0 / 2.54)
        return f"{val:.1f}pt ({cm:.2f}cm)"

    return t("margins_display",
             left=_fmt(margins.get("left", 0)),
             right=_fmt(margins.get("right", 0)),
             top=_fmt(margins.get("top", 0)),
             bottom=_fmt(margins.get("bottom", 0)))


def parse_rotation_list(
    rotation_list: list[dict],
    total_pages: int = 0,
) -> dict[int, float]:
    """Parse [[rotation]] config entries to {page_index: angle} map (0-based, sorted)."""
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
                    parts = val.split("-", 1)
                    if len(parts) == 2:
                        start_raw = parts[0].strip()
                        end_raw = parts[1].strip()
                        start = 1 if start_raw == "0" else int(start_raw)
                        end = total_pages if end_raw == "0" and total_pages > 0 else int(end_raw)
                        if end_raw == "0" and total_pages <= 0:
                            continue
                        if start <= end and end > 0:
                            range_pages = list(range(start, end + 1))
                            step = skip + 1
                            pages = [range_pages[i] for i in range(0, len(range_pages), step)]
                else:
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
