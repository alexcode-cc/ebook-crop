# 變更紀錄

本專案遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [Unreleased]

## [1.6.3] - 2026-03-05

### 修正

- **批次模式 PDF 重複處理**：Windows 上 glob 不區分大小寫，`*.pdf` 與 `*.PDF` 匹配相同檔案導致重複處理；改用 set 去重

## [1.6.2] - 2026-03-05

### 變更

- **國際化**：CLI 預設輸出改為英文訊息；使用 `--cht` 旗標顯示繁體中文訊息
- **i18n 模組**：新增 `ebook_crop/i18n.py`，含 EN/CHT 訊息字典與 `t()` 翻譯函式

## [1.6.1] - 2026-03-05

### 新增

- **自動偵測結果顯示**：處理完成後顯示每檔偵測摘要（裁切頁數、留白範圍）；使用 `-v` 可查看每頁詳細資訊

## [1.6.0] - 2026-03-05

### 新增

- **自動偵測留白**：`[auto_margins] enabled = true` 透過 PyMuPDF 文字/繪圖/圖片擷取分析每頁內容邊界，自動計算裁切量；啟用時 `[margins]` 棄用
- **偏移微調**：`[auto_margins]` 的 left/right/top/bottom 偏移值，用於自動偵測後的修正調整
- **automargin.py**：新增內容邊界偵測與自動裁切模組
- **自動偵測測試**：test_automargin.py 共 16 個測試，總測試數 124 個

## [1.5.1] - 2026-03-05

### 修正

- **測試目錄**：將測試資料從 `test/input/` 搬移至 `tests/input/`，`test/output/` 搬移至 `tests/output/`，統一使用 pytest 慣例目錄結構

## [1.5.0] - 2026-03-05

### 新增

- **pytest 框架**：完整測試套件，5 個測試模組共 108 個測試
- **Config 單元測試**：測試 `parse_rotation_list`、`format_rotation_display`、`format_margins_display`、`load_config`、`convert_margin_value`、`validate_config`（53 個測試）
- **Rotation 單元測試**：測試 `_get_rotated_page_rect`、寬高對調、`build_pdf_with_rotation`（15 個測試）
- **Crop 單元測試**：測試 `_apply_crop` 邊界條件、`crop_pdf`（11 個測試）
- **整合測試**：端對端流程 + CLI 整合測試（--version、--help、--dry-run、-v、-q）（12 個測試）
- **邊界測試**：單頁、小頁面、橫向、大檔案（50 頁）、旋轉邊界條件（17 個測試）
- **CI 測試流程**：pytest 加入 CI，於 Python 3.10/3.11/3.12 執行含覆蓋率
- **程式碼覆蓋率**：pytest-cov 整合，CI 中顯示覆蓋率報告（config 97%、crop 98%、rotation 100%）
- **tests/input/ 樣本**：`basic_5page.pdf`、`single_page.pdf`、`ten_pages.pdf`、`landscape.pdf`、`small_page.pdf` 及測試設定檔

### 變更

- **CI 工作流程**：新增 pytest 含覆蓋率

## [1.4.0] - 2026-03-05

### 新增

- **`--version` 旗標**：顯示目前版本
- **進度條**：批次處理時顯示 Rich 進度條
- **詳細/靜默模式**：`-v/--verbose` 與 `-q/--quiet` 旗標
- **預覽模式**：`--dry-run` 旗標，顯示設定與影響頁面，不實際處理
- **留白單位支援**：設定檔可使用 `"1cm"`、`"10mm"`、`"0.5in"`、`"0.5inch"`、`"36pt"`
- **設定檔驗證**：載入時驗證設定值，對無效值顯示明確錯誤訊息
- **彩色輸出**：警告黃色、錯誤紅色、成功綠色（透過 rich）
- **console.py 模組**：新增終端機輸出模組，統一彩色輸出、進度條、詳細/靜默模式

### 變更

- **CLI 輸出**：改用 rich 彩色格式

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

[Unreleased]: https://github.com/alexcode-cc/ebook-crop/compare/v1.6.3...HEAD
[1.6.3]: https://github.com/alexcode-cc/ebook-crop/compare/v1.6.2...v1.6.3
[1.6.2]: https://github.com/alexcode-cc/ebook-crop/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/alexcode-cc/ebook-crop/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/alexcode-cc/ebook-crop/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/alexcode-cc/ebook-crop/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/alexcode-cc/ebook-crop/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/alexcode-cc/ebook-crop/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.3.0
[1.2.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.2.0
[1.1.1]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.1
[1.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.1.0
[1.0.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v1.0.0
[0.1.0]: https://github.com/alexcode-cc/ebook-crop/releases/tag/v0.1.0
