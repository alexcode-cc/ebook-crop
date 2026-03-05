# GitHub 整合執行流程

本文件說明如何將 ebook-crop 專案與 GitHub 整合，並讓 CI 工作流程與 README 徽章正常運作。

---

## 1. 前置需求

- [Git](https://git-scm.com/) 已安裝
- [GitHub 帳號](https://github.com/)
- 本機專案已初始化 Git（`git init`）
- SSH 金鑰已設定並加入 GitHub（若使用 SSH 克隆）

---

## 2. 建立 GitHub 儲存庫

### 2.1 建立新儲存庫

1. 登入 GitHub，點擊右上角 **+** → **New repository**
2. 填寫：
   - **Repository name**：`ebook-crop`
   - **Description**：`PDF 電子書留白裁切工具，支援頁面旋轉任意角度，優化閱讀版面`
   - **Visibility**：Public（若為私有，CI 徽章可能無法顯示）
   - **不要**勾選「Add a README file」（本機已有）
3. 點擊 **Create repository**

### 2.2 取得儲存庫 URL

- **SSH**：`git@github.com:alexcode-cc/ebook-crop.git`
- **HTTPS**：`https://github.com/alexcode-cc/ebook-crop.git`

---

## 3. 設定遠端與推送

### 3.1 檢查遠端設定

```bash
git remote -v
```

若尚未設定 `origin`，執行：

```bash
git remote add origin git@github.com:alexcode-cc/ebook-crop.git
```

若需修改遠端 URL：

```bash
git remote set-url origin git@github.com:alexcode-cc/ebook-crop.git
```

### 3.2 推送至 GitHub

```bash
# 確認目前分支
git branch

# 推送 main 分支
git push -u origin main
```

首次推送時，若遠端為空儲存庫，Git 會上傳所有 commit 與檔案。

---

## 4. CI 工作流程執行

### 4.1 觸發時機

推送成功後，GitHub Actions 會自動觸發 CI 工作流程。本專案 CI 於以下情況執行：

| 觸發條件 | 說明 |
|----------|------|
| `push` 至 `main` 或 `develop` | 每次推送時執行 |
| `pull_request` 至 `main` 或 `develop` | 建立或更新 PR 時執行 |

### 4.2 工作流程內容

CI 包含兩個 job：

1. **Lint**：使用 Ruff 檢查程式碼風格
2. **Build & Verify**：在 Python 3.10、3.11、3.12 上安裝套件並驗證 CLI

### 4.3 查看執行結果

1. 開啟儲存庫頁面：`https://github.com/alexcode-cc/ebook-crop`
2. 點擊上方 **Actions** 分頁
3. 點選最新的 **CI** 工作流程執行
4. 可查看各 job 的日誌與狀態

### 4.4 徽章顯示條件

README 中的 CI 徽章需滿足以下條件才會正確顯示：

| 條件 | 說明 |
|------|------|
| 儲存庫已推送 | 程式碼已存在於 GitHub |
| 工作流程已執行 | 至少有一次 CI 執行紀錄 |
| 儲存庫為公開 | 私有儲存庫可能無法透過 shields.io 取得狀態 |
| 工作流程檔存在 | `.github/workflows/ci.yml` 已提交並推送 |

**重要**：首次推送後，請等待 1–2 分鐘讓 CI 完成執行，徽章才會顯示正確狀態（通過 / 失敗）。

---

## 5. 完整執行流程總覽

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 本機準備                                                      │
│     • git add / git commit 完成變更                               │
│     • git remote 已指向 GitHub 儲存庫                             │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 推送                                                          │
│     • git push -u origin main                                    │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. GitHub 接收                                                   │
│     • 儲存庫更新                                                  │
│     • 偵測到 .github/workflows/ci.yml                            │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Actions 觸發                                                  │
│     • 建立 CI 工作流程執行                                        │
│     • 排隊等候 runner                                             │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. CI 執行                                                       │
│     • Lint job：Ruff 檢查                                        │
│     • Build job：Python 3.10/3.11/3.12 建置驗證                   │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. 結果                                                          │
│     • 徽章更新（passing / failing）                               │
│     • PR 顯示 CI 狀態                                             │
│     • 可設定分支保護：需 CI 通過才能合併                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. 疑難排解

### 徽章顯示為破圖或「no status」

- **原因**：工作流程尚未執行、儲存庫為私有，或 shields.io 無法連線
- **處理**：
  1. 確認已執行 `git push origin main`
  2. 至 Actions 分頁確認 CI 是否已執行
  3. 若為私有儲存庫，可考慮改為公開，或移除 CI 徽章

### CI 執行失敗

- **Lint 失敗**：執行 `uv run ruff check .`  locally 修正
- **Build 失敗**：確認 `uv pip install -e .` 與 `ebook-crop --help` 在本機可正常執行

### 推送被拒絕（rejected）

- **原因**：遠端有本機沒有的 commit（例如在 GitHub 網頁新增了 README）
- **處理**：先 `git pull origin main --rebase`，再 `git push origin main`

---

## 7. 相關文件

- [GitHub 儲存庫設定指南](../.github/GITHUB_SETUP.md) — 進階儲存庫設定
- [技術分析](TECHNICAL_ANALYSIS.md) — 專案架構與技術說明
