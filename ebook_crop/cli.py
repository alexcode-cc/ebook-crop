"""命令列介面"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ebook_crop import __version__, config, crop, utils
from ebook_crop.console import NORMAL, QUIET, VERBOSE, AppConsole


def main() -> None:
    """主程式進入點"""
    parser = argparse.ArgumentParser(
        description="裁切 PDF 留白區域，支援頁面旋轉任意角度，優化電子書閱讀版面",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ebook-crop {__version__}",
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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="顯示詳細處理資訊",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="靜默模式，僅顯示錯誤訊息",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="預覽模式：顯示設定與影響頁面，不實際處理",
    )
    args = parser.parse_args()

    # 決定詳細程度
    if args.quiet and args.verbose:
        print("錯誤：-v 與 -q 不可同時使用", file=sys.stderr)
        sys.exit(1)

    verbosity = VERBOSE if args.verbose else (QUIET if args.quiet else NORMAL)
    con = AppConsole(verbosity)

    cfg = config.load_config(args.config)
    margins = cfg.get("margins", {})
    pages_config = cfg.get("pages", {})
    start_page = int(pages_config.get("start", 2))
    end_page = int(pages_config.get("end", 0))
    rotation_list = cfg.get("rotation", [])

    con.info(f"留白設定：{config.format_margins_display(margins)}")
    con.info(f"頁數範圍：從第 {start_page} 頁開始，"
             f"{'至最後一頁' if end_page == 0 else '最後一頁不裁切'}")
    if rotation_list:
        con.info(f"旋轉頁面：{config.format_rotation_display(rotation_list)}")

    con.verbose(f"設定檔：{args.config.resolve()}")

    if args.dry_run:
        _dry_run(con, args, margins, start_page, end_page, rotation_list)
        return

    if args.input is None and args.output is None:
        _batch_mode(con, args, margins, start_page, end_page, rotation_list)
    else:
        _single_mode(con, args, margins, start_page, end_page, rotation_list)


def _dry_run(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
) -> None:
    """預覽模式：顯示設定與影響頁面，不實際處理"""
    import fitz

    con.info("\n[bold cyan]--- 預覽模式（不會實際處理）---[/bold cyan]")

    if args.input is None and args.output is None:
        input_dir = args.input_dir.resolve()
        output_dir = args.output_dir.resolve()

        if not input_dir.exists():
            con.error(f"找不到輸入目錄 {input_dir}")
            sys.exit(1)

        pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))
        if not pdf_files:
            con.error(f"輸入目錄 {input_dir} 中沒有 PDF 檔案")
            sys.exit(1)

        con.info("模式：批次處理")
        con.info(f"輸入目錄：{input_dir}")
        con.info(f"輸出目錄：{output_dir}")
        con.info(f"檔案數量：{len(pdf_files)}")

        for pdf_path in pdf_files:
            doc = fitz.open(pdf_path)
            total = len(doc)
            doc.close()

            output_path = output_dir / pdf_path.name
            con.info(f"\n  {pdf_path.name} ({total} 頁) -> {output_path}")
            _show_affected_pages(con, total, start_page, end_page, rotation_list)
    else:
        if args.input is None:
            con.error("單檔模式需指定輸入檔案")
            sys.exit(1)

        if not args.input.exists():
            con.error(f"找不到輸入檔案 {args.input}")
            sys.exit(1)

        output_path = args.output
        if output_path is None:
            output_path = args.input.with_stem(f"{args.input.stem}_cropped")
        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        doc = fitz.open(args.input)
        total = len(doc)
        doc.close()

        con.info("模式：單檔處理")
        con.info(f"輸入：{args.input} ({total} 頁)")
        con.info(f"輸出：{output_path}")
        _show_affected_pages(con, total, start_page, end_page, rotation_list)


def _show_affected_pages(
    con: AppConsole,
    total_pages: int,
    start_page: int,
    end_page: int,
    rotation_list: list,
) -> None:
    """顯示受影響的頁面資訊"""
    start_idx = (start_page - 1) if start_page > 0 else 0
    end_idx = (total_pages - 2) if end_page == -1 else (total_pages - 1)
    crop_count = max(0, end_idx - start_idx + 1)
    con.info(f"  裁切頁面：第 {start_idx + 1} 至 {end_idx + 1} 頁（共 {crop_count} 頁）")

    if rotation_list:
        from ebook_crop import config as cfg_mod
        rotation_map = cfg_mod.parse_rotation_list(rotation_list, total_pages)
        if rotation_map:
            pages_str = ", ".join(str(i + 1) for i in rotation_map)
            con.info(f"  旋轉頁面：第 {pages_str} 頁（共 {len(rotation_map)} 頁）")


def _batch_mode(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
) -> None:
    """批次模式：處理 input/ 目錄內所有 PDF"""
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not input_dir.exists():
        con.error(f"找不到輸入目錄 {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))

    if not pdf_files:
        con.error(f"輸入目錄 {input_dir} 中沒有 PDF 檔案")
        sys.exit(1)

    con.info(f"批次模式：從 {input_dir} 處理 {len(pdf_files)} 個檔案至 {output_dir}")

    with con.progress(len(pdf_files), "批次裁切") as tracker:
        for input_path in pdf_files:
            output_path = output_dir / input_path.name
            con.verbose(f"裁切中：{input_path.name} -> {output_path}")
            crop.crop_pdf(input_path, output_path, margins, start_page, end_page, rotation_list)
            utils.save_config_to_output(args.config.resolve(), output_path)
            tracker.advance()

    con.success("完成！")


def _single_mode(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
) -> None:
    """單檔模式"""
    if args.input is None:
        con.error("單檔模式需指定輸入檔案")
        sys.exit(1)

    if not args.input.exists():
        con.error(f"找不到輸入檔案 {args.input}")
        sys.exit(1)

    output_path = args.output
    if output_path is None:
        output_path = args.input.with_stem(f"{args.input.stem}_cropped")

    if output_path.suffix.lower() != ".pdf":
        output_path = output_path.with_suffix(".pdf")

    con.safe_print(f"裁切中：{args.input} -> {output_path}")
    crop.crop_pdf(args.input, output_path, margins, start_page, end_page, rotation_list)
    utils.save_config_to_output(args.config.resolve(), output_path)
    con.success("完成！")
