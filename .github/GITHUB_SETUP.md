# GitHub Repository Setup Guide

This document describes recommended GitHub repository settings for project integration.

## Repository Settings

### General

1. **About**: Fill in description, website, topics
   - Description: `PDF ebook margin cropping tool with page rotation support for optimized reading layout`
   - Website: `https://github.com/alexcode-cc/ebook-crop#readme`
   - Topics: `pdf`, `ebook`, `crop`, `python`, `pymupdf`

2. **Features**
   - ✅ Issues
   - ✅ Discussions (optional, for Q&A)
   - ✅ Projects (optional)
   - ✅ Wiki (optional)

### Branch Protection (Branches → Add rule)

Recommended for `main`:

- **Require a pull request before merging**
  - Require approvals: 0 or 1 (depending on team size)
- **Require status checks to pass before merging**
  - Select CI workflow (e.g. `lint`, `build`)
- **Require branches to be up to date before merging**
- **Do not allow bypassing the above settings** (except admins)

### Secrets and variables

For future PyPI publishing:

- `PYPI_API_TOKEN`: PyPI API token for automated publishing

## Configured Integrations

| Item | Description |
|------|-------------|
| **CI** | `.github/workflows/ci.yml` — Lint (Ruff) + Build verification |
| **Dependabot** | `.github/dependabot.yml` — Weekly dependency updates |
| **Issue templates** | Bug report, feature request (English & Chinese) |
| **PR template** | Change type, checklist |
| **SECURITY.md** | Security policy and vulnerability reporting |
| **CODE_OF_CONDUCT.md** | Code of conduct |

## Suggested Labels

Add under Issues → Labels:

- `bug` — Bug reports
- `enhancement` — Feature requests
- `documentation` — Documentation
- `dependencies` — Dependency updates (Dependabot)
- `good first issue` — Good for newcomers
- `help wanted` — Help needed

## Release Workflow (optional)

For PyPI publishing, add `.github/workflows/release.yml` to trigger build and publish on Git tag creation.
