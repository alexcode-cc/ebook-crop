# ebook-crop

[![CI](https://img.shields.io/github/actions/workflow/status/alexcode-cc/ebook-crop/ci.yml?branch=main)](https://github.com/alexcode-cc/ebook-crop/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PDF 電子書留白裁切工具，去除大量上下左右留白，支援頁面旋轉任意角度，讓 PDF 中的文字顯示時不會因版面問題造成字體縮小，提升閱讀體驗。

## 功能特色

- **留白裁切**：可設定裁切上下左右留白區域大小
- **頁面旋轉**：支援掃描電子書角度修正，含任意角度
- **頁數範圍**：可指定裁切頁數範圍，封面與封底可選擇不裁切
- **批次處理**：可一次處理多個 PDF 檔案
- **設定追溯**：處理後保留裁切設定檔，便於日後重現

## 安裝

### 前置需求：安裝 uv

本專案推薦使用 [uv](https://github.com/astral-sh/uv)，這是一個極速的 Python 套件與專案管理工具。若尚未安裝 uv，請先執行：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows（PowerShell）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或透過 pip
pip install uv
```

> **uv** 整合了 `pip`、`pip-tools`、`virtualenv` 等工具的功能於一身，速度比 pip 快 10-100 倍。詳情請見 [uv 官方說明](https://github.com/astral-sh/uv)。

安裝 uv 後，克隆本專案：

```bash
git clone git@github.com:alexcode-cc/ebook-crop.git
cd ebook-crop
```

### 方式一：使用 uv run（推薦，不需啟動虛擬環境）

```bash
# 直接執行，uv 會自動建立虛擬環境並安裝依賴
uv run ebook-crop
```

常用指令：

```bash
# 批次模式
uv run ebook-crop

# 單檔模式
uv run ebook-crop input.pdf -o output.pdf

# 指定設定檔
uv run ebook-crop input.pdf -c config.toml -o output.pdf
```

### 方式二：使用 uv 建立虛擬環境後安裝

```bash
# 建立虛擬環境
uv venv

# 啟動虛擬環境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 啟動虛擬環境（Linux/macOS）
source .venv/bin/activate

# 安裝專案
uv pip install -e .

# 之後可直接使用 ebook-crop 指令
ebook-crop
```

### 方式三：使用 pip（不使用 uv）

```bash
pip install -e .
```

或從 PyPI 安裝（若已發布，安裝後可直接執行 `ebook-crop`）：

```bash
pip install ebook-crop
```

## 快速開始

1. 複製設定檔範本：

```bash
cp config-sample.toml config.toml
```

2. 依需求修改 `config.toml` 中的留白與裁切設定

3. 執行：

```bash
# 使用 uv run（推薦）
uv run ebook-crop                    # 批次模式：將 PDF 放入 input/ 目錄後執行
uv run ebook-crop input.pdf -o output.pdf   # 單檔模式

# 或已安裝後直接執行
ebook-crop
ebook-crop input.pdf -o output.pdf
```

## 設定檔 config.toml

留白單位：點 (points)，1 英吋 = 72 點

```toml
[margins]
left = 36
right = 36
top = 36
bottom = 36

[pages]
start = 2    # 開始裁切頁數，2=封面不裁切
end = 0      # 0=至最後一頁，-1=封底不裁切

# 頁面旋轉（掃描電子書角度修正）
[[rotation]]
pages = "3-0"
skip = 1
angle = -1
```

**留白單位換算**：1 公分 ≈ 28.35 點，0.5 英吋 = 36 點

## 使用方式

### 批次模式

不指定輸入與輸出檔案時，自動處理 `input/` 目錄內所有 PDF，以相同檔名輸出至 `output/` 目錄。

```bash
uv run ebook-crop
# 或已安裝後：ebook-crop
```

### 單檔模式

```bash
uv run ebook-crop input.pdf
uv run ebook-crop input.pdf -o output.pdf
uv run ebook-crop input.pdf -c my_config.toml
```

### 自訂目錄

```bash
uv run ebook-crop -i my_input -d my_output
```

### 參數說明

| 參數 | 說明 |
|------|------|
| `input` | 輸入 PDF（可省略，進入批次模式） |
| `-o, --output` | 輸出路徑 |
| `-c, --config` | 設定檔路徑 |
| `-i, --input-dir` | 批次輸入目錄 |
| `-d, --output-dir` | 批次輸出目錄 |

## 旋轉設定格式

| 格式 | 範例 | 說明 |
|------|------|------|
| 單頁 | `page = 3` | 第 3 頁 |
| 逗號 | `pages = "1,3,5"` | 指定多頁 |
| 範圍 | `pages = "3-9"` | 第 3 至 9 頁 |
| 至最後 | `pages = "3-0"` | 第 3 頁至最後一頁 |
| 全文件 | `pages = "0-0"` | 第 1 頁至最後一頁 |
| 跳頁 | `skip = 1` | 每隔一頁（3, 5, 7, 9） |

角度：正值=順時針、負值=逆時針

## 專案結構

```
ebook-crop/
├── config-sample.toml # 設定檔範本
├── config.toml        # 本機設定（Git 排除）
├── docs/              # 技術文件（英文）
├── docs-cht/          # 技術文件（繁體中文）
├── ebook_crop/        # 主程式模組
│   ├── __init__.py    # 版本號
│   ├── main.py        # 進入點
│   ├── cli.py         # 命令列介面
│   ├── config.py      # 設定載入與解析
│   ├── rotation.py    # 頁面旋轉
│   ├── crop.py        # 留白裁切
│   └── utils.py       # 共用工具
├── input/             # 批次輸入（Git 排除）
├── output/            # 批次輸出（Git 排除）
├── HISTORY.md         # 變更紀錄（英文）
├── HISTORY-CHT.md     # 變更紀錄（繁體中文）
├── LICENSE            # MIT 授權
├── README.md          # 專案說明（英文）
├── README-CHT.md      # 專案說明（繁體中文）
└── pyproject.toml
```

## 開發

### 貢獻

歡迎提交 Issue 與 Pull Request。請遵循 [CONTRIBUTING-CHT.md](CONTRIBUTING-CHT.md) 中的 Commit 規範，並遵守 [行為準則](CODE_OF_CONDUCT-CHT.md)。

### 繁體中文文件

- [貢獻指南](CONTRIBUTING-CHT.md)
- [行為準則](CODE_OF_CONDUCT-CHT.md)
- [安全政策](SECURITY-CHT.md)
- [變更紀錄](HISTORY-CHT.md)
- [技術文件](docs-cht/README.md)

### 技術文件

詳見 [docs-cht/TECHNICAL_ANALYSIS.md](docs-cht/TECHNICAL_ANALYSIS.md)。

## 授權

本專案採用 [MIT License](LICENSE) 授權。

## 連結

- **儲存庫**：<https://github.com/alexcode-cc/ebook-crop>
- **克隆**：`git clone git@github.com:alexcode-cc/ebook-crop.git`
