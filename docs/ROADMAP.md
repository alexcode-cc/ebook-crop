# Feature Roadmap

This document outlines planned features and improvement directions for ebook-crop, serving as a reference for future development.

---

## Phase 1: Quality & Testing Foundation

Establish automated testing to ensure stability before adding new features.

| Item | Description | Priority |
|------|-------------|----------|
| ✅ pytest framework | Set up pytest with test fixtures and sample PDFs | High |
| ✅ Config unit tests | Test `parse_rotation_list`, `format_rotation_display`, `load_config` | High |
| ✅ Rotation unit tests | Test `_get_rotated_page_rect`, dimension swap logic | High |
| ✅ Crop unit tests | Test `_apply_crop` boundary conditions (empty pages, zero margins) | High |
| ✅ Integration tests | End-to-end: load config, crop PDF, verify output | Medium |
| ✅ Edge case tests | Single page, empty file, encrypted PDF, very large files | Medium |
| ✅ CI test pipeline | Add pytest to CI workflow, run on Python 3.10/3.11/3.12 | High |
| ✅ Code coverage | Add coverage reporting to CI | Low |

---

## Phase 2: User Experience Improvements

Enhance CLI usability and feedback for daily use.

| Item | Description | Priority |
|------|-------------|----------|
| ✅ `--version` flag | Display current version (`ebook_crop.__version__`) | High |
| ✅ Progress bar | Show progress during batch processing (via `rich`) | Medium |
| ✅ Verbose/quiet mode | `-v` for detailed logs, `-q` for silent mode | Medium |
| ✅ Dry-run mode | `--dry-run` to preview settings and affected pages without processing | Medium |
| ✅ Margin unit support | Accept `cm`, `mm`, `in`/`inch`, `pt` in config (auto-convert to points) | Medium |
| ✅ Config validation | Validate config values on load; clear error messages for invalid margins, page ranges | Medium |
| ✅ Color output | Colored terminal output for warnings and errors (via `rich`) | Low |

---

## Phase 3: Core Feature Enhancements

Extend cropping and rotation capabilities.

| Item | Description | Priority |
|------|-------------|----------|
| ✅ Auto-detect margins | Analyze page content boundaries via PyMuPDF text/drawing extraction, suggest crop amounts | High |
| Per-page margins | Extend `[[margins]]` config for per-page or per-range margin overrides | Medium |
| Odd/even page margins | Different margins for odd and even pages (common in book-style scans) | Medium |
| Crop preview | Render a single page to image (PNG) showing crop/rotation result before full processing | Medium |
| tomllib support | Use Python 3.11+ stdlib `tomllib` when available, keep `tomli` as fallback for 3.10 | Low |
| Configurable garbage | Expose PyMuPDF `garbage` level (0-4) as a config option for output optimization | Low |
| Metadata preservation | Preserve or update PDF metadata (title, author, subject) during processing | Low |

---

## Phase 4: Advanced Features

Features for power users and large-scale processing.

| Item | Description | Priority |
|------|-------------|----------|
| Parallel batch processing | Use `concurrent.futures` for multi-file batch processing | Medium |
| Recursive directory | `-r` flag to process PDFs in subdirectories recursively | Medium |
| Output filename template | Configurable output naming pattern (e.g. `{stem}-cropped`, `{stem}-v2`) | Low |
| Watch mode | Monitor `input/` directory and auto-process new files | Low |
| Undo/restore | Keep original cropbox info for potential restoration | Low |
| Profile system | Named config profiles (e.g. `--profile textbook`, `--profile manga`) for common presets | Low |
| Page reordering | Reorder, remove, or duplicate pages during processing | Low |

---

## Phase 5: Ecosystem & Distribution

Expand project reach and accessibility.

| Item | Description | Priority |
|------|-------------|----------|
| PyPI publishing | GitHub Actions workflow for automated PyPI releases | High |
| Changelog automation | Generate changelog from conventional commits | Medium |
| GUI frontend | Optional graphical interface (Tkinter or web-based) for visual crop adjustment | Low |
| Docker image | Dockerfile for portable, dependency-free execution | Low |
| Plugin architecture | Hook system for custom pre/post-processing steps | Low |

---

## Design Principles

When implementing new features, follow these principles:

1. **Backward compatibility**: New config options must be optional; existing `config.toml` files should work without modification
2. **Minimal dependencies**: Prefer stdlib over third-party packages; new dependencies must be justified
3. **Fail gracefully**: Invalid config or unsupported PDF features should produce clear error messages, not crashes
4. **Bilingual maintenance**: All user-facing strings, docs, and commit messages support English and Traditional Chinese

---

## Language Versions

- **English** (current)
- [繁體中文 (docs-cht/)](../docs-cht/ROADMAP.md)
