# GitHub 儲存庫設定指南

本文件說明建議的 GitHub 儲存庫設定，以完善專案整合。

## 儲存庫設定 (Settings)

### 一般設定

1. **About**：填寫描述、網站、主題標籤
   - Description: `PDF 電子書留白裁切工具，優化閱讀版面`
   - Website: `https://github.com/alexcode-cc/ebook-crop#readme`
   - Topics: `pdf`, `ebook`, `crop`, `python`, `pymupdf`

2. **Features**
   - ✅ Issues
   - ✅ Discussions（可選，用於 Q&A）
   - ✅ Projects（可選）
   - ✅ Wiki（可選）

### 分支保護 (Branches → Add rule)

建議對 `main` 分支啟用：

- **Require a pull request before merging**
  - Require approvals: 0 或 1（依團隊規模）
- **Require status checks to pass before merging**
  - 勾選 CI workflow（如 `lint`、`build`）
- **Require branches to be up to date before merging**
- **Do not allow bypassing the above settings**（管理員除外）

### Secrets and variables

若未來需發布至 PyPI，可新增：

- `PYPI_API_TOKEN`：PyPI API token（用於自動發布）

## 已設定的整合

| 項目 | 說明 |
|------|------|
| **CI** | `.github/workflows/ci.yml` — Lint (Ruff) + Build 驗證 |
| **Dependabot** | `.github/dependabot.yml` — 每週檢查依賴更新 |
| **Issue 範本** | Bug 回報、功能建議 |
| **PR 範本** | 變更類型、檢查清單 |
| **SECURITY.md** | 安全政策與漏洞回報 |
| **CODE_OF_CONDUCT.md** | 行為準則 |

## 建議的 Labels

於 Issues → Labels 新增：

- `bug` — 錯誤回報
- `enhancement` — 功能建議
- `documentation` — 文件相關
- `dependencies` — 依賴更新（Dependabot 使用）
- `good first issue` — 適合新手
- `help wanted` — 需要協助

## 發布流程（可選）

若需發布至 PyPI，可新增 `.github/workflows/release.yml`，於建立 Git tag 時觸發建置與發布。
