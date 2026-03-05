# ebook-crop

[![CI](https://img.shields.io/github/actions/workflow/status/alexcode-cc/ebook-crop/ci.yml?branch=main)](https://github.com/alexcode-cc/ebook-crop/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PDF ebook margin cropping tool. Removes excessive top, bottom, left, and right margins, supports arbitrary-angle page rotation, and prevents font shrinking from layout issues for better reading experience.

**繁體中文**：請參閱 [README-CHT.md](README-CHT.md)

## Features

- **Margin cropping**: Configure crop amounts for top, bottom, left, and right margins
- **Page rotation**: Fix scan angles, including arbitrary angles
- **Page range**: Specify crop page range; optionally skip cover and back cover
- **Batch processing**: Process multiple PDFs at once
- **Auto-detect margins**: Automatically analyze page content boundaries and compute optimal crop margins per page
- **Config traceability**: Preserves crop settings after processing for future reproduction

## Installation

### Prerequisites: Install uv

This project recommends [uv](https://github.com/astral-sh/uv) — an extremely fast Python package and project manager. If you don't have uv installed yet:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

> **uv** replaces `pip`, `pip-tools`, `virtualenv`, and more in a single tool. See the [uv documentation](https://github.com/astral-sh/uv) for details.

After installing uv, clone this repository:

```bash
git clone git@github.com:alexcode-cc/ebook-crop.git
cd ebook-crop
```

### Option 1: uv run (recommended, no venv activation needed)

```bash
# uv automatically creates a venv and installs dependencies on first run
uv run ebook-crop
```

Common commands:

```bash
# Batch mode
uv run ebook-crop

# Single-file mode
uv run ebook-crop input.pdf -o output.pdf

# With config file
uv run ebook-crop input.pdf -c config.toml -o output.pdf
```

### Option 2: Install with uv into a virtual environment

```bash
# Create virtual environment
uv venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install project
uv pip install -e .

# Then use ebook-crop directly
ebook-crop
```

### Option 3: pip (without uv)

```bash
pip install -e .
```

Or from PyPI (if published):

```bash
pip install ebook-crop
```

## Quick Start

1. Copy config template:

```bash
cp config-sample.toml config.toml
```

2. Edit `config.toml` for margins and crop settings

3. Run:

```bash
# With uv run (recommended)
uv run ebook-crop                    # Batch: put PDFs in input/ then run
uv run ebook-crop input.pdf -o output.pdf   # Single file

# Or if installed
ebook-crop
ebook-crop input.pdf -o output.pdf
```

## Config: config.toml

Margin units: points (1 inch = 72 points). Supports unit suffixes: `cm`, `mm`, `in`/`inch`, `pt` (e.g. `"1cm"`, `"10mm"`, `"0.5in"`, `"36pt"`). Plain numbers are treated as points.

```toml
[margins]
left = 36
right = 36
top = "1cm"
bottom = "10mm"

[pages]
start = 2    # Start crop page, 2=skip cover
end = 0      # 0=to last page, -1=skip back cover

# Auto-detect margins (ignores [margins] when enabled)
[auto_margins]
enabled = true
left = 5      # fine-tune offset (points), positive=crop more
right = 5
top = 0
bottom = 0

# Page rotation (scan angle correction)
[[rotation]]
pages = "3-0"
skip = 1
angle = -1
```

**Unit conversion**: 1 cm ≈ 28.35 pt, 0.5 inch = 36 pt. Unit suffixes (`cm`, `mm`, `in`/`inch`, `pt`) are auto-converted to points.

## Usage

### Batch mode

Without input/output paths, processes all PDFs in `input/` and outputs to `output/` with same filenames.

```bash
uv run ebook-crop
# Or: ebook-crop
```

### Single-file mode

```bash
uv run ebook-crop input.pdf
uv run ebook-crop input.pdf -o output.pdf
uv run ebook-crop input.pdf -c my_config.toml
```

### Custom directories

```bash
uv run ebook-crop -i my_input -d my_output
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `input` | Input PDF (optional, enables batch mode if omitted) |
| `-o, --output` | Output path |
| `-c, --config` | Config file path |
| `-i, --input-dir` | Batch input directory |
| `-d, --output-dir` | Batch output directory |
| `--version` | Show current version |
| `-v, --verbose` | Verbose output with detailed logs |
| `-q, --quiet` | Quiet mode, suppress non-error output |
| `--dry-run` | Preview settings and affected pages without processing |

## Rotation config format

| Format | Example | Description |
|--------|---------|-------------|
| Single page | `page = 3` | Page 3 |
| Comma-separated | `pages = "1,3,5"` | Multiple pages |
| Range | `pages = "3-9"` | Pages 3 to 9 |
| To last | `pages = "3-0"` | Page 3 to last |
| Full document | `pages = "0-0"` | Page 1 to last |
| Skip | `skip = 1` | Every other page (3, 5, 7, 9) |

Angles: positive=clockwise, negative=counterclockwise

## Project structure

```
ebook-crop/
├── config-sample.toml # Config template
├── config.toml        # Local config (gitignored)
├── docs/              # Technical docs (English)
├── docs-cht/          # Technical docs (Traditional Chinese)
├── ebook_crop/        # Main module
│   ├── __init__.py    # Version
│   ├── main.py        # Entry point
│   ├── cli.py         # CLI
│   ├── config.py      # Config load and parse
│   ├── rotation.py    # Page rotation
│   ├── crop.py        # Margin crop
│   ├── automargin.py  # Auto-detect content boundaries and compute margins
│   ├── console.py     # Terminal output (colored output, progress bar, verbosity)
│   └── utils.py       # Shared utilities
├── tests/             # Test suite (pytest)
│   ├── conftest.py    # Shared fixtures
│   ├── test_config.py # Config unit tests
│   ├── test_rotation.py # Rotation unit tests
│   ├── test_crop.py   # Crop unit tests
│   ├── test_integration.py # Integration tests
│   ├── test_edge_cases.py # Edge case tests
│   ├── test_automargin.py # Auto-margin tests
│   ├── generate_samples.py # Sample PDF generator
│   ├── input/         # Sample PDFs and test configs
│   └── output/        # Test output (gitignored)
├── input/             # Batch input (gitignored)
├── output/            # Batch output (gitignored)
├── HISTORY.md         # Changelog (English)
├── LICENSE            # MIT
├── README.md          # Project readme (English)
├── README-CHT.md      # Project readme (Traditional Chinese)
└── pyproject.toml
```

## Development

### Run tests

```bash
uv run pytest --cov -v
```

### Contributing

Issues and Pull Requests are welcome from contributors worldwide. Please follow [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions and [Code of Conduct](CODE_OF_CONDUCT.md).

- **English docs**: [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [HISTORY.md](HISTORY.md)
- **Traditional Chinese (繁體中文)**: [README-CHT.md](README-CHT.md), [CONTRIBUTING-CHT.md](docs-cht/CONTRIBUTING-CHT.md), [docs-cht/](docs-cht/)

### Technical docs

See [docs/TECHNICAL_ANALYSIS.md](docs/TECHNICAL_ANALYSIS.md).

## License

[MIT License](LICENSE)

## Links

- **Repository**: https://github.com/alexcode-cc/ebook-crop
- **Clone**: `git clone git@github.com:alexcode-cc/ebook-crop.git`
