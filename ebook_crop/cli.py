"""Command-line interface"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ebook_crop import __version__, config, crop, utils
from ebook_crop.config import format_margins_display
from ebook_crop.console import NORMAL, QUIET, VERBOSE, AppConsole
from ebook_crop.i18n import set_lang, t


def _show_auto_results(con: AppConsole, results: list[dict], filename: str = "") -> None:
    """Show auto-detect margin results summary"""
    if not results:
        return

    cropped = [r for r in results if "margins" in r]
    skipped = [r for r in results if "skipped" in r]

    label = f"  [{filename}] " if filename else "  "

    if cropped:
        lefts = [r["margins"]["left"] for r in cropped]
        rights = [r["margins"]["right"] for r in cropped]
        tops = [r["margins"]["top"] for r in cropped]
        bottoms = [r["margins"]["bottom"] for r in cropped]

        skipped_info = t("auto_result_skipped", count=len(skipped)) if skipped else ""
        con.info(t("auto_result_summary", label=label, cropped=len(cropped),
                   skipped_info=skipped_info))
        con.info(t("auto_result_range", label=label,
                   lmin=min(lefts), lmax=max(lefts),
                   rmin=min(rights), rmax=max(rights),
                   tmin=min(tops), tmax=max(tops),
                   bmin=min(bottoms), bmax=max(bottoms)))

    for r in cropped:
        m = r["margins"]
        con.verbose(t("auto_page_detail", label=label, page=r["page"],
                      display=format_margins_display(m)))

    for r in skipped:
        con.verbose(t("auto_page_skipped", label=label, page=r["page"],
                      reason=r["skipped"]))


def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Crop PDF margins with page rotation for optimized ebook reading",
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
        help="Input PDF file (omit for batch mode on input/ directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF file (default: input_cropped.pdf)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.toml"),
        help="Config file path (default: config.toml)",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path("input"),
        help="Batch input directory (default: input)",
    )
    parser.add_argument(
        "-d",
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Batch output directory (default: output)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show detailed processing info",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Quiet mode, show errors only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview mode: show settings and affected pages without processing",
    )
    parser.add_argument(
        "--cht",
        action="store_true",
        default=False,
        help="Display messages in Traditional Chinese",
    )
    args = parser.parse_args()

    # Set language
    if args.cht:
        set_lang("cht")

    # Verbosity
    if args.quiet and args.verbose:
        print(t("err_vq_conflict"), file=sys.stderr)
        sys.exit(1)

    verbosity = VERBOSE if args.verbose else (QUIET if args.quiet else NORMAL)
    con = AppConsole(verbosity)

    cfg = config.load_config(args.config)
    margins = cfg.get("margins", {})
    pages_config = cfg.get("pages", {})
    start_page = int(pages_config.get("start", 2))
    end_page = int(pages_config.get("end", 0))
    rotation_list = cfg.get("rotation", [])
    auto_margins = cfg.get("_auto_margins")

    if auto_margins is not None:
        offsets = auto_margins.get("offsets", {})
        con.info(t("margin_mode_auto"))
        if any(v != 0 for v in offsets.values()):
            con.info(t("offset_adjustment", display=config.format_margins_display(offsets)))
    else:
        con.info(t("margin_settings", display=config.format_margins_display(margins)))

    end_desc = t("to_last_page") if end_page == 0 else t("skip_last_page")
    con.info(t("page_range", start=start_page, end_desc=end_desc))
    if rotation_list:
        con.info(t("rotation_pages", display=config.format_rotation_display(rotation_list)))

    con.verbose(t("config_file", path=args.config.resolve()))

    if args.dry_run:
        _dry_run(con, args, margins, start_page, end_page, rotation_list, auto_margins)
        return

    if args.input is None and args.output is None:
        _batch_mode(con, args, margins, start_page, end_page, rotation_list, auto_margins)
    else:
        _single_mode(con, args, margins, start_page, end_page, rotation_list, auto_margins)


def _dry_run(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
    auto_margins: dict | None = None,
) -> None:
    """Preview mode: show settings and affected pages without processing"""
    import fitz

    con.info(t("dry_run_header"))

    if args.input is None and args.output is None:
        input_dir = args.input_dir.resolve()
        output_dir = args.output_dir.resolve()

        if not input_dir.exists():
            con.error(t("err_input_dir_not_found", path=input_dir))
            sys.exit(1)

        pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))
        if not pdf_files:
            con.error(t("err_no_pdf_files", path=input_dir))
            sys.exit(1)

        con.info(t("mode_batch"))
        con.info(t("input_dir", path=input_dir))
        con.info(t("output_dir", path=output_dir))
        con.info(t("file_count", count=len(pdf_files)))

        for pdf_path in pdf_files:
            doc = fitz.open(pdf_path)
            total = len(doc)
            doc.close()

            output_path = output_dir / pdf_path.name
            con.info(f"\n  {pdf_path.name} ({total} pages) -> {output_path}")
            _show_affected_pages(con, total, start_page, end_page, rotation_list)
    else:
        if args.input is None:
            con.error(t("err_single_needs_input"))
            sys.exit(1)

        if not args.input.exists():
            con.error(t("err_input_not_found", path=args.input))
            sys.exit(1)

        output_path = args.output
        if output_path is None:
            output_path = args.input.with_stem(f"{args.input.stem}_cropped")
        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        doc = fitz.open(args.input)
        total = len(doc)
        doc.close()

        con.info(t("mode_single"))
        con.info(t("input_file", path=args.input, total=total))
        con.info(t("output_file", path=output_path))
        _show_affected_pages(con, total, start_page, end_page, rotation_list)


def _show_affected_pages(
    con: AppConsole,
    total_pages: int,
    start_page: int,
    end_page: int,
    rotation_list: list,
) -> None:
    """Show affected pages info"""
    start_idx = (start_page - 1) if start_page > 0 else 0
    end_idx = (total_pages - 2) if end_page == -1 else (total_pages - 1)
    crop_count = max(0, end_idx - start_idx + 1)
    con.info(t("crop_pages", start=start_idx + 1, end=end_idx + 1, count=crop_count))

    if rotation_list:
        from ebook_crop import config as cfg_mod
        rotation_map = cfg_mod.parse_rotation_list(rotation_list, total_pages)
        if rotation_map:
            pages_str = ", ".join(str(i + 1) for i in rotation_map)
            con.info(t("rotation_detail", pages=pages_str, count=len(rotation_map)))


def _batch_mode(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
    auto_margins: dict | None = None,
) -> None:
    """Batch mode: process all PDFs in input/ directory"""
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not input_dir.exists():
        con.error(t("err_input_dir_not_found", path=input_dir))
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))

    if not pdf_files:
        con.error(t("err_no_pdf_files", path=input_dir))
        sys.exit(1)

    con.info(t("batch_info", count=len(pdf_files), src=input_dir, dst=output_dir))

    all_results: list[tuple[str, list[dict]]] = []

    with con.progress(len(pdf_files), t("batch_progress")) as tracker:
        for input_path in pdf_files:
            output_path = output_dir / input_path.name
            con.verbose(t("cropping", src=input_path.name, dst=output_path))
            results = crop.crop_pdf(input_path, output_path, margins, start_page, end_page,
                                    rotation_list, auto_margins)
            utils.save_config_to_output(args.config.resolve(), output_path)
            if results is not None:
                all_results.append((input_path.name, results))
            tracker.advance()

    if all_results:
        for filename, results in all_results:
            _show_auto_results(con, results, filename)

    con.success(t("done"))


def _single_mode(
    con: AppConsole,
    args: argparse.Namespace,
    margins: dict,
    start_page: int,
    end_page: int,
    rotation_list: list,
    auto_margins: dict | None = None,
) -> None:
    """Single-file mode"""
    if args.input is None:
        con.error(t("err_single_needs_input"))
        sys.exit(1)

    if not args.input.exists():
        con.error(t("err_input_not_found", path=args.input))
        sys.exit(1)

    output_path = args.output
    if output_path is None:
        output_path = args.input.with_stem(f"{args.input.stem}_cropped")

    if output_path.suffix.lower() != ".pdf":
        output_path = output_path.with_suffix(".pdf")

    con.safe_print(t("cropping", src=args.input, dst=output_path))
    results = crop.crop_pdf(args.input, output_path, margins, start_page, end_page,
                            rotation_list, auto_margins)
    utils.save_config_to_output(args.config.resolve(), output_path)

    if results is not None:
        _show_auto_results(con, results)

    con.success(t("done"))
