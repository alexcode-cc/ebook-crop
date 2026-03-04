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
        help="輸入 PDF 檔案路徑",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="輸出 PDF 檔案路徑（預設：輸入檔名_cropped.pdf）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.toml"),
        help="設定檔路徑（預設：config.toml）",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    margins = config.get("margins", {})

    if not args.input.exists():
        print(f"錯誤：找不到輸入檔案 {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if output_path is None:
        output_path = args.input.with_stem(f"{args.input.stem}_cropped")

    if output_path.suffix.lower() != ".pdf":
        output_path = output_path.with_suffix(".pdf")

    print(f"裁切中：{args.input} -> {output_path}")
    print(f"留白設定：左 {margins.get('left', 0)}pt, 右 {margins.get('right', 0)}pt, "
          f"上 {margins.get('top', 0)}pt, 下 {margins.get('bottom', 0)}pt")

    crop_pdf(args.input, output_path, margins)
    print("完成！")


if __name__ == "__main__":
    main()
