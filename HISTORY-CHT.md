# 變更紀錄

本專案遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [Unreleased]

## [1.3.0] - 2026-03-05

### 新增

- **功能藍圖**：新增 `docs/ROADMAP.md` 與 `docs-cht/ROADMAP.md`，包含分階段開發計畫，涵蓋測試、體驗、核心功能、進階功能與生態系
- **CLAUDE.md**：新增 Claude Code 輔助指引檔案

### 變更

- **技術文件**：更新擴充建議（第 6 節）改為引用 ROADMAP，檔案清單新增相關文件
- **文件索引**：`docs/README.md` 與 `docs-cht/README.md` 新增 ROADMAP 連結
- **安全政策**：更新支援版本表至 1.3.x

## [1.2.0] - 2026-03-05

### 新增

- **國際化**：新增英文文件，支援國際社群貢獻者
- **docs-cht/**：繁體中文技術文件目錄
- **docs/**：英文技術文件
- ***-CHT.md**：專案根目錄繁體中文文件（README-CHT、CONTRIBUTING-CHT、SECURITY-CHT、CODE_OF_CONDUCT-CHT、HISTORY-CHT）

## [1.1.1] - 2026-03-05

### 修正

- **CI**：使用 `uv run ebook-crop` 取代直接執行，修正 GitHub Actions 中 PATH 問題

## [1.1.0] - 2026-03-05

### 重構

- **模組化拆分**：將 `main.py` 拆為 `cli.py`、`config.py`、`rotation.py`、`crop.py`、`utils.py`，各職責分離

## [1.0.0] - 2026-03-05

### 新增

- **留白裁切**：可設定上下左右留白裁切量，優化電子書閱讀版面
- **裁切頁數範圍**：支援開始/結束頁數設定，封面與封底可選擇不裁切
- **頁面旋轉**：支援指定多頁進行角度旋轉（含任意角度）
- **旋轉設定格式**：
  - 單頁：`page = 3`
  - 多頁：`pages = "1,3,5"` 或 `pages = [1, 3, 5]`
  - 範圍：`pages = "3-9"`
  - 至最後一頁：`pages = "3-0"`（0 表示最後一頁）
  - 全文件：`pages = "0-0"`
  - 跳頁：`skip = 1` 表示每隔一頁
- **批次模式**：無參數時自動處理 `input/` 目錄內所有 PDF
- **設定追溯**：處理後將 config 複製為 `檔名.toml` 至輸出目錄
- **設定檔範本**：`config-sample.toml`，本機 `config.toml` 自 Git 排除

### 修正

- 修正 Windows 主控台 Unicode 編碼問題（`_safe_print`）
- 修正程式無法正常退出與資源釋放（try/finally、garbage=1）
- 修正開始裁切頁數說明（0 與 1 皆表示封面也裁切）

### 技術

- Python 3.10+
- PyMuPDF 1.24+
- TOML 設定檔（tomli）
- uv 環境管理

---

## [0.1.0] - 初始版本

- 基礎 PDF 留白裁切功能
- config.toml 留白設定
- 單檔與批次處理

[Unreleased]: https://github.com/alexcode-cc/ebook-crop/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.3.0
[1.2.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.2.0
[1.1.1]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.1
[1.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.0
[1.0.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.0.0
[0.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v0.1.0
