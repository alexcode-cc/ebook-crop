# Contributing Guide

Contributions from developers worldwide are welcome. This project supports both English and Traditional Chinese documentation.

- **English** (this file)
- **繁體中文**: [CONTRIBUTING-CHT.md](docs-cht/CONTRIBUTING-CHT.md)

## Git Commit Message Conventions

This project follows [AngularJS Git Commit Message Conventions](https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Rules

- **Max 100 characters per line**
- **subject**: Imperative mood, present tense (e.g. "add" not "added"), no leading capital, no trailing period
- **body**: Describe what and why (not how), imperative mood
- **footer**: Optional, for breaking changes or issue references

### Type

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Code style (no logic change, e.g. indentation, semicolons) |
| refactor | Refactoring |
| test | Tests |
| chore | Build, tooling, maintenance |

### Scope (optional)

Module or area, e.g. `cli`, `config`, `crop`, `rotation`, `utils`.

### Examples

```
feat(pdf): add PDF margin cropping

Implement config.toml loading and PyMuPDF crop logic,
support custom top/bottom/left/right margin crop amounts.
```

```
fix(cli): fix default output filename

When input path has no extension, output filename incorrectly
appended _cropped. Fix stem and suffix handling.
```

```
docs: update README installation

Add uv venv setup and Windows PowerShell activation commands.
```

```
chore: initialize project structure

Add pyproject.toml, config.toml, and ebook_crop module.
```
