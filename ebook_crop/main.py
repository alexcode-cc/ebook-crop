"""PDF 電子書留白裁切主程式"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import fitz  # PyMuPDF
import tomli


def _safe_print(msg: str) -> None:
    """輸出至 stdout，遇編碼錯誤時改用 ASCII 替代字元"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def save_config_to_output(config_path: Path, output_pdf_path: Path) -> None:
    """
    將使用的 config.toml 複製到輸出目錄，檔名為處理文件的檔名。

    Args:
        config_path: 設定檔路徑
        output_pdf_path: 輸出 PDF 路徑（用於決定檔名與目錄）
    """
    output_dir = output_pdf_path.parent
    config_copy_name = f"{output_pdf_path.stem}.toml"
    config_copy_path = output_dir / config_copy_name
    shutil.copy2(config_path, config_copy_path)


def load_config(config_path: Path) -> dict:
    """載入 config.toml 設定檔"""
    if not config_path.exists():
        print(f"錯誤：找不到設定檔 {config_path}", file=sys.stderr)
        sample = config_path.parent / "config-sample.toml"
        if sample.exists():
            print(f"提示：可複製 {sample} 為 {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomli.load(f)


def crop_pdf(
    input_path: Path,
    output_path: Path,
    margins: dict[str, float],
    start_page: int = 2,
    end_page: int = 0,
) -> None:
    """
    裁切 PDF 留白區域。

    Args:
        input_path: 輸入 PDF 路徑
        output_path: 輸出 PDF 路徑
        margins: 留白裁切量 dict，包含 left, right, top, bottom（單位：點）
        start_page: 開始裁切頁數（1-based），0=從第1頁，2=封面不裁切
        end_page: 結束裁切頁數，0=裁切到最後一頁，-1=最後一頁不裁切
    """
    left = margins.get("left", 0)
    right = margins.get("right", 0)
    top = margins.get("top", 0)
    bottom = margins.get("bottom", 0)

    doc = fitz.open(input_path)
    total_pages = len(doc)

    # 1-based 轉 0-based：start_page=2 -> 從 index 1 開始裁切
    start_index = (start_page - 1) if start_page > 0 else 0
    # end_page=0 -> 裁切到最後；end_page=-1 -> 裁切到倒數第二頁
    end_index = (total_pages - 2) if end_page == -1 else (total_pages - 1)

    for page_num in range(total_pages):
        # 不在裁切範圍內的頁面跳過
        if page_num < start_index or page_num > end_index:
            continue

        page = doc[page_num]
        rect = page.rect

        # 計算裁切後的顯示區域
        crop_rect = fitz.Rect(
            left,
            top,
            rect.width - right,
            rect.height - bottom,
        )

        # 確保裁切區域有效
        if crop_rect.width <= 0 or crop_rect.height <= 0:
            print(
                f"警告：第 {page_num + 1} 頁裁切區域無效，跳過裁切",
                file=sys.stderr,
            )
            continue

        page.set_cropbox(crop_rect)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


def main() -> None:
    """主程式進入點"""
    parser = argparse.ArgumentParser(
        description="裁切 PDF 留白區域，優化電子書閱讀版面",
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="輸入 PDF 檔案路徑（省略時處理 input/ 目錄內所有 PDF）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="輸出 PDF 檔案路徑（單檔模式預設：輸入檔名_cropped.pdf）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.toml"),
        help="設定檔路徑（預設：config.toml）",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path("input"),
        help="批次模式輸入目錄（預設：input）",
    )
    parser.add_argument(
        "-d",
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="批次模式輸出目錄（預設：output）",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    margins = config.get("margins", {})
    pages_config = config.get("pages", {})
    start_page = int(pages_config.get("start", 2))
    end_page = int(pages_config.get("end", 0))

    print(f"留白設定：左 {margins.get('left', 0)}pt, 右 {margins.get('right', 0)}pt, "
          f"上 {margins.get('top', 0)}pt, 下 {margins.get('bottom', 0)}pt")
    print(f"頁數範圍：從第 {start_page} 頁開始，"
          f"{'至最後一頁' if end_page == 0 else '最後一頁不裁切'}")

    if args.input is None and args.output is None:
        # 批次模式：處理 input/ 目錄內所有 PDF
        input_dir = args.input_dir.resolve()
        output_dir = args.output_dir.resolve()

        if not input_dir.exists():
            print(f"錯誤：找不到輸入目錄 {input_dir}", file=sys.stderr)
            sys.exit(1)

        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))

        if not pdf_files:
            print(f"輸入目錄 {input_dir} 中沒有 PDF 檔案", file=sys.stderr)
            sys.exit(1)

        print(f"批次模式：從 {input_dir} 處理 {len(pdf_files)} 個檔案至 {output_dir}")
        for input_path in pdf_files:
            output_path = output_dir / input_path.name
            _safe_print(f"裁切中：{input_path.name} -> {output_path}")
            crop_pdf(input_path, output_path, margins, start_page, end_page)
            save_config_to_output(args.config.resolve(), output_path)
        print("完成！")
    else:
        # 單檔模式
        if args.input is None:
            print("錯誤：單檔模式需指定輸入檔案", file=sys.stderr)
            sys.exit(1)

        if not args.input.exists():
            print(f"錯誤：找不到輸入檔案 {args.input}", file=sys.stderr)
            sys.exit(1)

        output_path = args.output
        if output_path is None:
            output_path = args.input.with_stem(f"{args.input.stem}_cropped")

        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        _safe_print(f"裁切中：{args.input} -> {output_path}")
        crop_pdf(args.input, output_path, margins, start_page, end_page)
        save_config_to_output(args.config.resolve(), output_path)
        print("完成！")


if __name__ == "__main__":
    main()
