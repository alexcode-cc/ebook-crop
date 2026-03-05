# 貢獻指南

歡迎全球開發者貢獻本專案。文件提供雙語版本。

- **繁體中文**（本頁）
- **English**: [CONTRIBUTING.md](CONTRIBUTING.md)

## Git Commit 訊息規範

本專案採用 [AngularJS Git Commit Message Conventions](https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit) 規範，提交訊息可使用英文或繁體中文。

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 規則

- **每行不超過 100 字元**
- **subject**：使用祈使句、現在式（如「新增」而非「新增了」），首字不大寫，句尾不加句點
- **body**：說明變更內容與原因（非做法），使用祈使句
- **footer**：可選，用於重大變更或關聯 issue

### Type 類型

| Type | 說明 |
|------|------|
| feat | 新功能 |
| fix | 錯誤修復 |
| docs | 文件變更 |
| style | 程式碼格式（不影響邏輯，如縮排、分號） |
| refactor | 重構 |
| test | 測試相關 |
| chore | 建置、工具、維護 |

### Scope 範圍（可選）

指定變更的模組或區域，例如：`cli`、`config`、`crop`、`rotation`、`utils`。

### 範例

```
feat(pdf): 新增 PDF 留白裁切功能

實作 config.toml 設定檔讀取與 PyMuPDF 裁切邏輯，
支援自訂上下左右留白裁切量。
```

```
fix(cli): 修正輸出檔名預設值錯誤

當輸入路徑不含副檔名時，輸出檔名會錯誤附加 _cropped，
改為正確處理 stem 與 suffix。
```

```
docs: 更新 README 安裝說明

補充 uv 虛擬環境建立步驟與 Windows PowerShell 啟動指令。
```

```
chore: 初始化專案結構

建立 pyproject.toml、config.toml 與 ebook_crop 模組。
```
