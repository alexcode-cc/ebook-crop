"""PDF 電子書留白裁切主程式"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF
import tomli


def load_config(config_path: Path) -> dict:
    """載入 config.toml 設定檔"""
    if not config_path.exists():
        print(f"錯誤：找不到設定檔 {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomli.load(f)


def crop_pdf(
    input_path: Path,
    output_path: Path,
    margins: dict[str, float],
) -> None:
    """
    裁切 PDF 留白區域。

    Args:
        input_path: 輸入 PDF 路徑
        output_path: 輸出 PDF 路徑
        margins: 留白裁切量 dict，包含 left, right, top, bottom（單位：點）
    """
    left = margins.get("left", 0)
    right = margins.get("right", 0)
    top = margins.get("top", 0)
    bottom = margins.get("bottom", 0)

    doc = fitz.open(input_path)
    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc[page_num]
        rect = page.rect

        # 計算裁切後的顯示區域
        # 裁切左、上：起點往內移
        # 裁切右、下：終點往內移
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

    print(f"留白設定：左 {margins.get('left', 0)}pt, 右 {margins.get('right', 0)}pt, "
          f"上 {margins.get('top', 0)}pt, 下 {margins.get('bottom', 0)}pt")

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
            print(f"裁切中：{input_path.name} -> {output_path}")
            crop_pdf(input_path, output_path, margins)
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

        print(f"裁切中：{args.input} -> {output_path}")
        crop_pdf(args.input, output_path, margins)
        print("完成！")


if __name__ == "__main__":
    main()
