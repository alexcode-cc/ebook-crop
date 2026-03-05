# GitHub Integration Workflow

This document explains how to integrate the ebook-crop project with GitHub and ensure CI workflows and README badges work correctly.

---

## 1. Prerequisites

- [Git](https://git-scm.com/) installed
- [GitHub account](https://github.com/)
- Local project initialized with Git (`git init`)
- SSH key configured and added to GitHub (if using SSH clone)

---

## 2. Create GitHub Repository

### 2.1 Create New Repository

1. Log in to GitHub, click **+** → **New repository**
2. Fill in:
   - **Repository name**: `ebook-crop`
   - **Description**: `PDF ebook margin cropping tool with page rotation support for optimized reading layout`
   - **Visibility**: Public (private repos may not display CI badges correctly)
   - **Do not** check "Add a README file" (local project already has one)
3. Click **Create repository**

### 2.2 Get Repository URL

- **SSH**: `git@github.com:alexcode-cc/ebook-crop.git`
- **HTTPS**: `https://github.com/alexcode-cc/ebook-crop.git`

---

## 3. Configure Remote and Push

### 3.1 Check Remote Configuration

```bash
git remote -v
```

If `origin` is not set:

```bash
git remote add origin git@github.com:alexcode-cc/ebook-crop.git
```

To change remote URL:

```bash
git remote set-url origin git@github.com:alexcode-cc/ebook-crop.git
```

### 3.2 Push to GitHub

```bash
# Verify current branch
git branch

# Push main branch
git push -u origin main
```

On first push, if the remote is an empty repository, Git will upload all commits and files.

---

## 4. CI Workflow Execution

### 4.1 Trigger Conditions

After a successful push, GitHub Actions automatically triggers the CI workflow. This project's CI runs on:

| Trigger | Description |
|---------|-------------|
| `push` to `main` or `develop` | Runs on every push |
| `pull_request` to `main` or `develop` | Runs when creating or updating a PR |

### 4.2 Workflow Contents

CI includes two jobs:

1. **Lint**: Ruff checks code style
2. **Build & Verify**: Installs package and verifies CLI on Python 3.10, 3.11, 3.12

### 4.3 View Execution Results

1. Open repository: `https://github.com/alexcode-cc/ebook-crop`
2. Click **Actions** tab
3. Select the latest **CI** workflow run
4. View logs and status for each job

### 4.4 Badge Display Requirements

README CI badge requires these conditions to display correctly:

| Condition | Description |
|-----------|-------------|
| Repository pushed | Code exists on GitHub |
| Workflow executed | At least one CI run recorded |
| Repository public | Private repos may not expose status via shields.io |
| Workflow file exists | `.github/workflows/ci.yml` committed and pushed |

**Important**: After first push, wait 1–2 minutes for CI to complete before the badge shows correct status (passing/failing).

---

## 5. Complete Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Local Preparation                                             │
│     • git add / git commit changes                                │
│     • git remote points to GitHub repository                      │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Push                                                          │
│     • git push -u origin main                                    │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. GitHub Receives                                               │
│     • Repository updated                                          │
│     • Detects .github/workflows/ci.yml                           │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Actions Trigger                                               │
│     • Creates CI workflow run                                    │
│     • Queues for runner                                          │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. CI Execution                                                  │
│     • Lint job: Ruff check                                       │
│     • Build job: Python 3.10/3.11/3.12 build verification        │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Results                                                       │
│     • Badge updates (passing/failing)                             │
│     • PR shows CI status                                          │
│     • Branch protection: CI must pass to merge                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Troubleshooting

### Badge shows broken image or "no status"

- **Cause**: Workflow not yet run, private repository, or shields.io unreachable
- **Fix**:
  1. Confirm `git push origin main` executed
  2. Check Actions tab for CI run
  3. For private repos, consider making public or removing CI badge

### CI execution fails

- **Lint failure**: Run `uv run ruff check .` locally to fix
- **Build failure**: Verify `uv pip install -e .` and `ebook-crop --help` work locally

### Push rejected

- **Cause**: Remote has commits not in local (e.g., README added on GitHub)
- **Fix**: Run `git pull origin main --rebase`, then `git push origin main`

---

## 7. Related Documentation

- [GitHub Repository Setup Guide](../.github/GITHUB_SETUP.md) — Advanced repository configuration
- [Technical Analysis](TECHNICAL_ANALYSIS.md) — Project architecture and technical details
