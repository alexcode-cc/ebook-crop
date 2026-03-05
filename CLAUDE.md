# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ebook-crop (v1.6.1) is a Python CLI tool for cropping PDF ebook margins and applying arbitrary-angle page rotation. It uses PyMuPDF (`fitz`) for PDF manipulation, `tomli` for TOML config parsing, and `rich` for colored terminal output and progress bars.

## Common Commands

```bash
# Run the tool (uv auto-creates venv)
uv run ebook-crop                              # Batch mode: input/ -> output/
uv run ebook-crop input.pdf -o output.pdf      # Single file

# Lint
uv run ruff check .

# Run tests
uv run pytest --cov --cov-report=term-missing -v

# Install dependencies
uv sync --locked --all-extras
```

Tests use `pytest` with `pytest-cov`. Test fixtures and sample PDFs are in `tests/input/`, test output goes to `tests/output/` (gitignored). CI runs `ruff check`, `pytest --cov`, and `ebook-crop --help` on Python 3.10/3.11/3.12.

## Architecture

Entry point: `ebook_crop/main.py` -> `cli.py:main()`.

Processing pipeline:
1. **cli.py** — Parses CLI args (`argparse`), loads config, dispatches batch or single-file mode
2. **config.py** — Loads `config.toml` via `tomli`, parses `[[rotation]]` entries into a `{page_index: angle}` map (0-based)
3. **crop.py** — Orchestrates: opens PDF, applies rotation (if any) then margin cropping via `set_cropbox()`
4. **rotation.py** — Rebuilds PDF with rotated pages using `show_pdf_page()` (non-rotated pages copied via `insert_pdf`)
5. **utils.py** — `_safe_print()` for Unicode-safe output, `save_config_to_output()` copies config alongside output PDF
6. **console.py** — Terminal output module: colored output (warnings yellow, errors red, success green), rich progress bar for batch processing, verbosity control (`-v`/`-q`)
7. **automargin.py** — Auto-detect content boundaries via PyMuPDF text/drawing/image extraction, compute per-page crop margins with optional offset adjustments

Key design details:
- Rotation config uses 1-based page numbers; `parse_rotation_list()` converts to 0-based indices
- `pages = "3-0"` means "page 3 to last page" (0 = last page sentinel)
- Config file is copied next to output PDF for traceability (`{pdf_stem}.toml`)
- `rotation.py` rebuilds the entire document page-by-page when any rotation is needed

## Config Format

Units are PDF points (72pt = 1 inch) by default. Margin values also accept unit suffixes: `"1cm"`, `"10mm"`, `"0.5in"`, `"0.5inch"`, `"36pt"`. See `config-sample.toml` for the template.

Auto-detect margins: Set `[auto_margins] enabled = true` to auto-detect content boundaries per page. When enabled, `[margins]` is ignored. Offset values (`left/right/top/bottom`) fine-tune the auto-detected crop (positive = crop more inward, negative = crop less).

## Conventions

- Python 3.10+, managed with `uv` and `hatchling` build backend
- Linting: `ruff` with rules E, F, I, N, W; line length 100
- Commit messages: Angular convention, bilingual (English or Traditional Chinese)
- Bilingual docs: English primary (`README.md`, `CONTRIBUTING.md`), Traditional Chinese variants (`*-CHT.md`)
