"""命令列介面"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ebook_crop import config, crop, utils


def main() -> None:
    """主程式進入點"""
    parser = argparse.ArgumentParser(
        description="裁切 PDF 留白區域，支援頁面旋轉任意角度，優化電子書閱讀版面",
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

    cfg = config.load_config(args.config)
    margins = cfg.get("margins", {})
    pages_config = cfg.get("pages", {})
    start_page = int(pages_config.get("start", 2))
    end_page = int(pages_config.get("end", 0))
    rotation_list = cfg.get("rotation", [])

    print(f"留白設定：左 {margins.get('left', 0)}pt, 右 {margins.get('right', 0)}pt, "
          f"上 {margins.get('top', 0)}pt, 下 {margins.get('bottom', 0)}pt")
    print(f"頁數範圍：從第 {start_page} 頁開始，"
          f"{'至最後一頁' if end_page == 0 else '最後一頁不裁切'}")
    if rotation_list:
        print(f"旋轉頁面：{config.format_rotation_display(rotation_list)}")

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
            utils._safe_print(f"裁切中：{input_path.name} -> {output_path}")
            crop.crop_pdf(input_path, output_path, margins, start_page, end_page, rotation_list)
            utils.save_config_to_output(args.config.resolve(), output_path)
        print("完成！")
        sys.stdout.flush()
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

        utils._safe_print(f"裁切中：{args.input} -> {output_path}")
        crop.crop_pdf(args.input, output_path, margins, start_page, end_page, rotation_list)
        utils.save_config_to_output(args.config.resolve(), output_path)
        print("完成！")
        sys.stdout.flush()
