"""config.py unit tests"""

from __future__ import annotations

import pytest

from ebook_crop.config import (
    convert_margin_value,
    format_margins_display,
    format_rotation_display,
    load_config,
    parse_rotation_list,
    validate_config,
)

# --- convert_margin_value ---


class TestConvertMarginValue:
    def test_int(self):
        assert convert_margin_value(36) == 36.0

    def test_float(self):
        assert convert_margin_value(28.35) == 28.35

    def test_zero(self):
        assert convert_margin_value(0) == 0.0

    def test_str_no_unit(self):
        assert convert_margin_value("36") == 36.0

    def test_str_pt(self):
        assert convert_margin_value("36pt") == 36.0

    def test_str_cm(self):
        result = convert_margin_value("1cm")
        assert abs(result - 72.0 / 2.54) < 0.01

    def test_str_mm(self):
        result = convert_margin_value("10mm")
        assert abs(result - 72.0 / 25.4 * 10) < 0.01

    def test_str_in(self):
        assert convert_margin_value("1in") == 72.0

    def test_str_inch(self):
        assert convert_margin_value("0.5inch") == 36.0

    def test_str_with_spaces(self):
        assert convert_margin_value(" 36 pt ") == 36.0

    def test_case_insensitive(self):
        assert convert_margin_value("1CM") == convert_margin_value("1cm")

    def test_invalid_string(self):
        with pytest.raises(ValueError, match="Invalid margin value"):
            convert_margin_value("abc")

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid margin value"):
            convert_margin_value([1, 2])

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Invalid margin value"):
            convert_margin_value("10px")


# --- validate_config ---


class TestValidateConfig:
    def test_valid_minimal(self):
        cfg = {}
        assert validate_config(cfg) == []

    def test_valid_full(self):
        cfg = {
            "margins": {"left": 36, "right": 36, "top": 36, "bottom": 36},
            "pages": {"start": 2, "end": 0},
            "rotation": [{"page": 3, "angle": 90}],
        }
        assert validate_config(cfg) == []

    def test_valid_units(self):
        cfg = {
            "margins": {"left": "1cm", "right": "10mm", "top": "0.5in", "bottom": "36pt"},
        }
        assert validate_config(cfg) == []

    def test_negative_margin(self):
        cfg = {"margins": {"left": -10}}
        errors = validate_config(cfg)
        assert len(errors) == 1
        assert "negative" in errors[0].lower() or "must not" in errors[0].lower()

    def test_invalid_margin_string(self):
        cfg = {"margins": {"left": "bad"}}
        errors = validate_config(cfg)
        assert len(errors) == 1
        assert "margin" in errors[0].lower() or "invalid" in errors[0].lower()

    def test_invalid_pages_start(self):
        cfg = {"pages": {"start": -1}}
        errors = validate_config(cfg)
        assert any("start" in e.lower() for e in errors)

    def test_invalid_pages_end(self):
        cfg = {"pages": {"end": 5}}
        errors = validate_config(cfg)
        assert any("end" in e.lower() for e in errors)

    def test_rotation_missing_page(self):
        cfg = {"rotation": [{"angle": 90}]}
        errors = validate_config(cfg)
        assert any("page" in e.lower() for e in errors)

    def test_rotation_missing_angle(self):
        cfg = {"rotation": [{"page": 3}]}
        errors = validate_config(cfg)
        assert any("angle" in e.lower() for e in errors)

    def test_rotation_invalid_angle(self):
        cfg = {"rotation": [{"page": 3, "angle": "bad"}]}
        errors = validate_config(cfg)
        assert any("angle" in e.lower() and "number" in e.lower() for e in errors)

    def test_multiple_errors(self):
        cfg = {
            "margins": {"left": "bad"},
            "pages": {"start": -1, "end": 5},
        }
        errors = validate_config(cfg)
        assert len(errors) >= 3


# --- load_config ---


class TestLoadConfig:
    def test_load_basic(self, basic_config_path):
        cfg = load_config(basic_config_path)
        assert cfg["margins"]["left"] == 36.0
        assert cfg["margins"]["right"] == 36.0
        assert cfg["pages"]["start"] == 2
        assert cfg["pages"]["end"] == 0

    def test_load_units(self, units_config_path):
        cfg = load_config(units_config_path)
        assert abs(cfg["margins"]["left"] - 72.0 / 2.54) < 0.01  # 1cm
        assert abs(cfg["margins"]["right"] - 72.0 / 25.4 * 10) < 0.01  # 10mm
        assert cfg["margins"]["top"] == 36.0  # 0.5in
        assert cfg["margins"]["bottom"] == 36.0  # 36pt

    def test_load_rotation(self, rotation_config_path):
        cfg = load_config(rotation_config_path)
        assert len(cfg["rotation"]) == 2
        assert cfg["rotation"][0]["page"] == 3
        assert cfg["rotation"][0]["angle"] == 90

    def test_missing_file(self, tmp_path):
        with pytest.raises(SystemExit):
            load_config(tmp_path / "nonexistent.toml")

    def test_invalid_config(self, tmp_path):
        bad_config = tmp_path / "bad.toml"
        bad_config.write_text('[margins]\nleft = "invalid_unit"\n')
        with pytest.raises(SystemExit):
            load_config(bad_config)


# --- parse_rotation_list ---


class TestParseRotationList:
    def test_single_page(self):
        result = parse_rotation_list([{"page": 3, "angle": 90}])
        assert result == {2: 90.0}

    def test_pages_comma(self):
        result = parse_rotation_list([{"pages": "1,3,5", "angle": 45}])
        assert result == {0: 45.0, 2: 45.0, 4: 45.0}

    def test_pages_range(self):
        result = parse_rotation_list([{"pages": "3-5", "angle": -1}])
        assert result == {2: -1.0, 3: -1.0, 4: -1.0}

    def test_pages_to_last(self):
        result = parse_rotation_list([{"pages": "3-0", "angle": 90}], total_pages=5)
        assert result == {2: 90.0, 3: 90.0, 4: 90.0}

    def test_pages_to_last_no_total(self):
        result = parse_rotation_list([{"pages": "3-0", "angle": 90}], total_pages=0)
        assert result == {}

    def test_pages_full_doc(self):
        result = parse_rotation_list([{"pages": "0-0", "angle": 1}], total_pages=3)
        assert result == {0: 1.0, 1: 1.0, 2: 1.0}

    def test_pages_skip(self):
        result = parse_rotation_list(
            [{"pages": "1-7", "skip": 1, "angle": 90}]
        )
        assert result == {0: 90.0, 2: 90.0, 4: 90.0, 6: 90.0}

    def test_pages_array(self):
        result = parse_rotation_list([{"pages": [2, 4, 6], "angle": 30}])
        assert result == {1: 30.0, 3: 30.0, 5: 30.0}

    def test_pages_int(self):
        result = parse_rotation_list([{"pages": 5, "angle": 90}])
        assert result == {4: 90.0}

    def test_negative_skip(self):
        result = parse_rotation_list([{"pages": "1-3", "skip": -1, "angle": 10}])
        assert result == {0: 10.0, 1: 10.0, 2: 10.0}

    def test_sorted_output(self):
        result = parse_rotation_list([
            {"page": 5, "angle": 90},
            {"page": 1, "angle": 45},
            {"page": 3, "angle": -1},
        ])
        keys = list(result.keys())
        assert keys == [0, 2, 4]

    def test_empty_list(self):
        assert parse_rotation_list([]) == {}

    def test_multiple_entries(self):
        result = parse_rotation_list([
            {"page": 1, "angle": 90},
            {"pages": "3-5", "angle": -1},
        ], total_pages=5)
        assert result == {0: 90.0, 2: -1.0, 3: -1.0, 4: -1.0}


# --- format_rotation_display ---


class TestFormatRotationDisplay:
    def test_single_page(self):
        result = format_rotation_display([{"page": 3, "angle": 90}])
        assert "3" in result
        assert "90" in result

    def test_range_to_last(self):
        result = format_rotation_display([{"pages": "3-0", "angle": -1}])
        assert "last" in result.lower() or "to last" in result.lower()

    def test_range_with_skip(self):
        result = format_rotation_display([{"pages": "3-9", "skip": 1, "angle": 2}])
        assert "every" in result.lower() or "1" in result

    def test_comma_pages(self):
        result = format_rotation_display([{"pages": "1,3,5", "angle": 45}])
        assert "1,3,5" in result

    def test_array_pages(self):
        result = format_rotation_display([{"pages": [2, 4], "angle": 10}])
        assert "2,4" in result

    def test_multiple_entries(self):
        result = format_rotation_display([
            {"page": 1, "angle": 90},
            {"page": 5, "angle": -1},
        ])
        assert ";" in result

    def test_no_page_or_pages(self):
        result = format_rotation_display([{"angle": 90}])
        assert result == ""


# --- format_margins_display ---


class TestFormatMarginsDisplay:
    def test_basic(self):
        result = format_margins_display({"left": 36.0, "right": 36.0, "top": 36.0, "bottom": 36.0})
        assert "L " in result or "left" in result.lower()
        assert "R " in result or "right" in result.lower()
        assert "36.0pt" in result

    def test_zero_margins(self):
        result = format_margins_display({"left": 0, "right": 0, "top": 0, "bottom": 0})
        assert "0.0pt" in result

    def test_missing_keys(self):
        result = format_margins_display({})
        assert "0.0pt" in result
