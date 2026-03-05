# Changelog

This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.4.0] - 2026-03-05

### Added

- **`--version` flag**: Display current version (`ebook_crop.__version__`)
- **Progress bar**: Rich progress bar during batch processing
- **Verbose/quiet mode**: `-v/--verbose` for detailed logs, `-q/--quiet` for silent mode
- **Dry-run mode**: `--dry-run` to preview settings and affected pages without processing
- **Margin unit support**: Config accepts `cm`, `mm`, `in`/`inch`, `pt` suffixes (e.g. `"1cm"`, `"10mm"`, `"0.5in"`, `"36pt"`) in addition to plain numbers
- **Config validation**: Validates config values on load with clear error messages for invalid margins, page ranges
- **Colored terminal output**: Warnings in yellow, errors in red, success in green (via `rich`)
- **`console.py` module**: Terminal output module handling colored output, progress bar, and verbosity control

### Changed

- **CLI output**: Now uses `rich` for colored formatting

## [1.3.0] - 2026-03-05

### Added

- **Feature roadmap**: `docs/ROADMAP.md` and `docs-cht/ROADMAP.md` with phased development plans covering testing, UX, core features, advanced features, and ecosystem
- **CLAUDE.md**: Claude Code guidance file for AI-assisted development

### Changed

- **Technical docs**: Updated extension suggestions (section 6) to reference ROADMAP, added file list entries for new docs
- **Documentation index**: Added ROADMAP links to `docs/README.md` and `docs-cht/README.md`
- **Security policy**: Updated supported versions table for 1.3.x

## [1.2.0] - 2026-03-05

### Added

- **Internationalization**: English documentation for international contributors
- **docs-cht/**: Traditional Chinese technical documentation directory
- **docs/**: English technical documentation
- ***-CHT.md**: Root-level Traditional Chinese docs (README-CHT, CONTRIBUTING-CHT, SECURITY-CHT, CODE_OF_CONDUCT-CHT, HISTORY-CHT)

## [1.1.1] - 2026-03-05

### Fixed

- **CI**: Use `uv run ebook-crop` instead of direct execution to fix PATH in GitHub Actions

## [1.1.0] - 2026-03-05

### Refactored

- **Modular split**: Split `main.py` into `cli.py`, `config.py`, `rotation.py`, `crop.py`, `utils.py` with clear responsibilities

## [1.0.0] - 2026-03-05

### Added

- **Margin cropping**: Configurable top/bottom/left/right margin crop amounts for better ebook layout
- **Page range**: Start/end page settings; optionally skip cover and back cover
- **Page rotation**: Arbitrary-angle rotation for specified pages
- **Rotation config format**:
  - Single: `page = 3`
  - Multiple: `pages = "1,3,5"` or `pages = [1, 3, 5]`
  - Range: `pages = "3-9"`
  - To last: `pages = "3-0"` (0 = last page)
  - Full: `pages = "0-0"`
  - Skip: `skip = 1` for every other page
- **Batch mode**: Processes all PDFs in `input/` when no args given
- **Config traceability**: Copies config as `filename.toml` to output directory
- **Config template**: `config-sample.toml`; local `config.toml` gitignored

### Fixed

- Windows console Unicode encoding (`_safe_print`)
- Process exit and resource cleanup (try/finally, garbage=1)
- Start page description (0 and 1 both mean crop from cover)

### Technical

- Python 3.10+
- PyMuPDF 1.24+
- TOML config (tomli)
- uv environment management

---

## [0.1.0] - Initial release

- Basic PDF margin cropping
- config.toml margin settings
- Single-file and batch processing

[Unreleased]: https://github.com/alexcode-cc/ebook-crop/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/alexcode-cc/ebook-crop/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.3.0
[1.2.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.2.0
[1.1.1]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.1
[1.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.0
[1.0.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.0.0
[0.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v0.1.0
