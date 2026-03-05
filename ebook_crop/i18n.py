"""Internationalization (i18n) module for CLI messages"""

from __future__ import annotations

_lang: str = "en"

_MESSAGES: dict[str, dict[str, str]] = {
    # CLI description and help
    "cli_desc": {
        "en": "Crop PDF margins with arbitrary-angle page rotation for optimized ebook reading",
        "cht": "裁切 PDF 留白區域，支援頁面旋轉任意角度，優化電子書閱讀版面",
    },
    "help_input": {
        "en": "Input PDF file (omit for batch mode on input/ directory)",
        "cht": "輸入 PDF 檔案路徑（省略時處理 input/ 目錄內所有 PDF）",
    },
    "help_output": {
        "en": "Output PDF file (default: input_cropped.pdf)",
        "cht": "輸出 PDF 檔案路徑（單檔模式預設：輸入檔名_cropped.pdf）",
    },
    "help_config": {
        "en": "Config file path (default: config.toml)",
        "cht": "設定檔路徑（預設：config.toml）",
    },
    "help_input_dir": {
        "en": "Batch input directory (default: input)",
        "cht": "批次模式輸入目錄（預設：input）",
    },
    "help_output_dir": {
        "en": "Batch output directory (default: output)",
        "cht": "批次模式輸出目錄（預設：output）",
    },
    "help_verbose": {
        "en": "Show detailed processing info",
        "cht": "顯示詳細處理資訊",
    },
    "help_quiet": {
        "en": "Quiet mode, show errors only",
        "cht": "靜默模式，僅顯示錯誤訊息",
    },
    "help_dry_run": {
        "en": "Preview mode: show settings and affected pages without processing",
        "cht": "預覽模式：顯示設定與影響頁面，不實際處理",
    },
    "help_cht": {
        "en": "Display messages in Traditional Chinese",
        "cht": "顯示繁體中文訊息",
    },
    # CLI runtime messages
    "err_vq_conflict": {
        "en": "Error: -v and -q cannot be used together",
        "cht": "錯誤：-v 與 -q 不可同時使用",
    },
    "margin_mode_auto": {
        "en": "Margin mode: [bold]auto-detect[/bold]",
        "cht": "留白模式：[bold]自動偵測[/bold]",
    },
    "offset_adjustment": {
        "en": "Offset adjustment: {display}",
        "cht": "偏移微調：{display}",
    },
    "margin_settings": {
        "en": "Margin settings: {display}",
        "cht": "留白設定：{display}",
    },
    "page_range": {
        "en": "Page range: from page {start}, {end_desc}",
        "cht": "頁數範圍：從第 {start} 頁開始，{end_desc}",
    },
    "to_last_page": {
        "en": "to last page",
        "cht": "至最後一頁",
    },
    "skip_last_page": {
        "en": "last page excluded",
        "cht": "最後一頁不裁切",
    },
    "rotation_pages": {
        "en": "Rotation: {display}",
        "cht": "旋轉頁面：{display}",
    },
    "config_file": {
        "en": "Config: {path}",
        "cht": "設定檔：{path}",
    },
    "cropping": {
        "en": "Cropping: {src} -> {dst}",
        "cht": "裁切中：{src} -> {dst}",
    },
    "done": {
        "en": "Done!",
        "cht": "完成！",
    },
    "batch_progress": {
        "en": "Batch cropping",
        "cht": "批次裁切",
    },
    # Dry-run
    "dry_run_header": {
        "en": "\n[bold cyan]--- Preview mode (no changes will be made) ---[/bold cyan]",
        "cht": "\n[bold cyan]--- 預覽模式（不會實際處理）---[/bold cyan]",
    },
    "mode_batch": {
        "en": "Mode: batch processing",
        "cht": "模式：批次處理",
    },
    "mode_single": {
        "en": "Mode: single file",
        "cht": "模式：單檔處理",
    },
    "input_dir": {
        "en": "Input directory: {path}",
        "cht": "輸入目錄：{path}",
    },
    "output_dir": {
        "en": "Output directory: {path}",
        "cht": "輸出目錄：{path}",
    },
    "file_count": {
        "en": "File count: {count}",
        "cht": "檔案數量：{count}",
    },
    "input_file": {
        "en": "Input: {path} ({total} pages)",
        "cht": "輸入：{path}（{total} 頁）",
    },
    "output_file": {
        "en": "Output: {path}",
        "cht": "輸出：{path}",
    },
    "crop_pages": {
        "en": "  Crop pages: {start} to {end} ({count} pages)",
        "cht": "  裁切頁面：第 {start} 至 {end} 頁（共 {count} 頁）",
    },
    "rotation_detail": {
        "en": "  Rotation: page {pages} ({count} pages)",
        "cht": "  旋轉頁面：第 {pages} 頁（共 {count} 頁）",
    },
    "batch_info": {
        "en": "Batch mode: processing {count} files from {src} to {dst}",
        "cht": "批次模式：從 {src} 處理 {count} 個檔案至 {dst}",
    },
    # Errors
    "err_input_dir_not_found": {
        "en": "Input directory not found: {path}",
        "cht": "找不到輸入目錄 {path}",
    },
    "err_no_pdf_files": {
        "en": "No PDF files in input directory {path}",
        "cht": "輸入目錄 {path} 中沒有 PDF 檔案",
    },
    "err_single_needs_input": {
        "en": "Single-file mode requires an input file",
        "cht": "單檔模式需指定輸入檔案",
    },
    "err_input_not_found": {
        "en": "Input file not found: {path}",
        "cht": "找不到輸入檔案 {path}",
    },
    # Auto-margin results
    "auto_result_summary": {
        "en": "{label}Auto-detect result: {cropped} pages cropped{skipped_info}",
        "cht": "{label}自動偵測結果：{cropped} 頁裁切{skipped_info}",
    },
    "auto_result_skipped": {
        "en": ", {count} pages skipped",
        "cht": "、{count} 頁跳過",
    },
    "auto_result_range": {
        "en": (
            "{label}Margin range (pt): L {lmin:.1f}~{lmax:.1f}, "
            "R {rmin:.1f}~{rmax:.1f}, "
            "T {tmin:.1f}~{tmax:.1f}, "
            "B {bmin:.1f}~{bmax:.1f}"
        ),
        "cht": (
            "{label}留白範圍（點）：左 {lmin:.1f}~{lmax:.1f}, "
            "右 {rmin:.1f}~{rmax:.1f}, "
            "上 {tmin:.1f}~{tmax:.1f}, "
            "下 {bmin:.1f}~{bmax:.1f}"
        ),
    },
    "auto_page_detail": {
        "en": "{label}Page {page}: {display}",
        "cht": "{label}第 {page} 頁：{display}",
    },
    "auto_page_skipped": {
        "en": "{label}Page {page}: skipped ({reason})",
        "cht": "{label}第 {page} 頁：跳過（{reason}）",
    },
    # Console prefixes
    "warning_prefix": {
        "en": "Warning: ",
        "cht": "警告：",
    },
    "error_prefix": {
        "en": "Error: ",
        "cht": "錯誤：",
    },
    # Warnings in crop/automargin
    "warn_invalid_crop": {
        "en": "Warning: page {page} crop area invalid, skipping",
        "cht": "警告：第 {page} 頁裁切區域無效，跳過裁切",
    },
    "warn_no_content": {
        "en": "Warning: page {page} no content detected, skipping",
        "cht": "警告：第 {page} 頁無法偵測內容邊界，跳過裁切",
    },
    "warn_auto_invalid_crop": {
        "en": "Warning: page {page} auto-crop area invalid, skipping",
        "cht": "警告：第 {page} 頁自動裁切區域無效，跳過裁切",
    },
    "skip_no_content": {
        "en": "no content",
        "cht": "無內容",
    },
    "skip_invalid_crop": {
        "en": "invalid crop area",
        "cht": "裁切區域無效",
    },
    "warn_rotation_out_of_range": {
        "en": "Warning: rotation page {page} out of range ({total} pages), skipping",
        "cht": "警告：旋轉頁碼 {page} 超出範圍（共 {total} 頁），跳過",
    },
    # Config errors
    "err_config_not_found": {
        "en": "Error: config file not found: {path}",
        "cht": "錯誤：找不到設定檔 {path}",
    },
    "hint_copy_sample": {
        "en": "Hint: copy {sample} to {config}",
        "cht": "提示：可複製 {sample} 為 {config}",
    },
    "err_config_validation": {
        "en": "Error: config validation failed:",
        "cht": "錯誤：設定檔驗證失敗：",
    },
    "err_margin_negative": {
        "en": "[margins] {key} must not be negative: {val}",
        "cht": "[margins] {key} 不可為負值：{val}",
    },
    "err_invalid_margin": {
        "en": "Invalid margin value{label}: {value!r}, expected number or unit string",
        "cht": "無效的留白值{label}：{value!r}，需為數字或含單位的字串",
    },
    "err_invalid_margin_format": {
        "en": (
            "Invalid margin value{label}: {value!r}, "
            "supported: 36, 1cm, 10mm, 0.5in, 0.5inch, 36pt"
        ),
        "cht": (
            "無效的留白值{label}：{value!r}，"
            "支援格式：36、1cm、10mm、0.5in、0.5inch、36pt"
        ),
    },
    "err_pages_start": {
        "en": "[pages] start must be non-negative integer, got: {val!r}",
        "cht": "[pages] start 需為非負整數，目前為：{val!r}",
    },
    "err_pages_end": {
        "en": "[pages] end must be 0 (to last page) or -1 (exclude last), got: {val!r}",
        "cht": "[pages] end 需為 0（至最後一頁）或 -1（不含最後一頁），目前為：{val!r}",
    },
    "err_rotation_not_array": {
        "en": "[[rotation]] must be an array, got: {type}",
        "cht": "[[rotation]] 需為陣列，目前為：{type}",
    },
    "err_rotation_not_table": {
        "en": "[[rotation]] entry {idx} must be a table, got: {type}",
        "cht": "[[rotation]] 第 {idx} 筆需為表格，目前為：{type}",
    },
    "err_rotation_no_page": {
        "en": "[[rotation]] entry {idx} missing page or pages field",
        "cht": "[[rotation]] 第 {idx} 筆缺少 page 或 pages 欄位",
    },
    "err_rotation_no_angle": {
        "en": "[[rotation]] entry {idx} missing angle field",
        "cht": "[[rotation]] 第 {idx} 筆缺少 angle 欄位",
    },
    "err_rotation_bad_angle": {
        "en": "[[rotation]] entry {idx} angle must be a number, got: {val!r}",
        "cht": "[[rotation]] 第 {idx} 筆 angle 需為數字，目前為：{val!r}",
    },
    # Rotation display
    "page_n": {
        "en": "page {val}",
        "cht": "第 {val} 頁",
    },
    "page_range_to_last": {
        "en": "page {start} to last",
        "cht": "第 {start} 頁至最後一頁",
    },
    "every_n_pages": {
        "en": " (every {skip} pages)",
        "cht": "（每隔{skip}頁）",
    },
    # Margins display
    "margins_display": {
        "en": "L {left}, R {right}, T {top}, B {bottom}",
        "cht": "左 {left}, 右 {right}, 上 {top}, 下 {bottom}",
    },
}


def set_lang(lang: str) -> None:
    """Set the global language ('en' or 'cht')"""
    global _lang
    _lang = lang


def get_lang() -> str:
    """Get the current language"""
    return _lang


def t(msg_key: str, **kwargs) -> str:
    """Get translated message. Use kwargs for format placeholders."""
    msgs = _MESSAGES.get(msg_key)
    if msgs is None:
        return msg_key
    msg = msgs.get(_lang, msgs.get("en", msg_key))
    if kwargs:
        return msg.format(**kwargs)
    return msg
