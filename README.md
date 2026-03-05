# ebook-crop

PDF 電子書留白裁切工具，去除大量上下左右留白，讓 PDF 中的文字顯示時不會因版面問題造成字體縮小，提升閱讀體驗。

## 功能特色

- 可設定裁切上下左右留白區域大小
- 支援頁面旋轉（掃描電子書角度修正，含任意角度）
- 透過 `config.toml` 集中管理設定
- 使用 PyMuPDF 高效處理 PDF

## 環境需求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（Python 套件與環境管理工具）

## 安裝與設定

### 1. 使用 uv 建立虛擬環境

```bash
# 建立 venv 虛擬環境
uv venv

# 啟動虛擬環境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 啟動虛擬環境（Windows CMD）
.venv\Scripts\activate.bat

# 啟動虛擬環境（Linux/macOS）
source .venv/bin/activate
```

### 2. 安裝依賴套件

```bash
uv pip install -e .
```

## 設定檔 config.toml

首次使用請複製 `config-sample.toml` 為 `config.toml` 後依需求修改。`config.toml` 已自 Git 排除，可存放本機專屬設定。

留白單位：點 (points)，1 英吋 = 72 點

```toml
[margins]
left = 36    # 左側裁切量（點）
right = 36   # 右側裁切量（點）
top = 36     # 上方裁切量（點）
bottom = 36  # 下方裁切量（點）

[pages]
start = 2    # 開始裁切頁數（1-based），0或1=封面也裁切，2=封面不裁切
end = 0      # 結束裁切頁數，0=裁切到最後一頁，-1=封底不裁切

# 頁面旋轉（掃描電子書角度修正，支援任意角度）
# pages 支援：逗號 "1,3,5"、範圍 "3-9"、"3-0"（0=最後一頁）、"0-0"（全文件）、skip=1 每隔一頁
# [[rotation]]
# pages = "3-9"
# skip = 1
# angle = -1
# [[rotation]]
# page = 12
# angle = 90
```

**留白單位換算參考：**
- 1 公分 ≈ 28.35 點
- 1 英吋 = 72 點
- 0.5 英吋 = 36 點

## 使用方式

### 批次模式（無參數）

不指定輸入與輸出檔案時，自動處理 `input/` 目錄內所有 PDF，以相同檔名輸出至 `output/` 目錄。每個處理後的 PDF 會同時儲存對應的裁切設定檔（`檔名.toml`）於輸出目錄，便於日後追溯。

```bash
# 將 PDF 放入 input/ 目錄後執行
ebook-crop
```

### 單檔模式

```bash
# 基本用法（輸出為 輸入檔名_cropped.pdf）
ebook-crop input.pdf

# 指定輸出檔名
ebook-crop input.pdf -o output.pdf

# 使用自訂設定檔
ebook-crop input.pdf -c my_config.toml
```

### 自訂批次目錄

```bash
ebook-crop -i my_input -d my_output
```

## 專案結構

```
ebook-crop/
├── input/             # 批次模式輸入目錄（Git 排除）
├── output/            # 批次模式輸出目錄（含 PDF 與對應 .toml 設定檔，Git 排除）
├── config-sample.toml # 設定檔範本（複製為 config.toml 使用）
├── config.toml        # 本機設定（Git 排除）
├── pyproject.toml   # 專案與依賴設定
├── README.md
└── ebook_crop/
    ├── __init__.py
    └── main.py      # 主程式
```
