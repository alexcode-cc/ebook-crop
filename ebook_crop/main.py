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


def _format_rotation_display(rotation_list: list[dict]) -> str:
    """將 rotation 設定格式化為顯示字串，含頁次與角度。"""
    parts: list[str] = []
    for r in rotation_list:
        angle = float(r.get("angle", 0))
        angle_str = f"{angle:g}°"

        if "pages" in r:
            val = r["pages"]
            skip = int(r.get("skip", 0))
            if isinstance(val, str):
                val = val.strip()
                if "-" in val and "," not in val:
                    parts_range = val.split("-", 1)
                    start_raw, end_raw = parts_range[0].strip(), parts_range[1].strip()
                    if end_raw == "0":
                        pages_str = f"第 {start_raw if start_raw != '0' else '1'} 頁至最後一頁"
                    else:
                        pages_str = f"第 {val} 頁"
                    if skip > 0:
                        pages_str += f"（每隔{skip}頁）"
                else:
                    pages_str = f"第 {val} 頁"
            elif isinstance(val, (list, tuple)):
                pages_str = f"第 {','.join(str(x) for x in val)} 頁"
            else:
                pages_str = f"第 {val} 頁"
        elif "page" in r:
            p = int(r["page"])
            pages_str = f"第 {p} 頁"
        else:
            continue

        parts.append(f"{pages_str} {angle_str}")
    return "；".join(parts)


def _parse_rotation_list(
    rotation_list: list[dict],
    total_pages: int = 0,
) -> dict[int, float]:
    """
    解析 [[rotation]] 設定，支援：
    - page：單頁
    - pages：多頁，可為 "1,3,5"、"3-9" 或 "3-0"（0=最後一頁）、"0-0"（全文件）
    - skip：搭配範圍使用，每隔 N 頁取一頁
    回傳 {page_index: angle}，0-based，已排序。
    """
    rotation_map: dict[int, float] = {}
    for r in rotation_list:
        a = float(r.get("angle", 0))
        skip = int(r.get("skip", 0))
        if skip < 0:
            skip = 0
        pages: list[int] = []

        if "pages" in r:
            val = r["pages"]
            if isinstance(val, int):
                if val > 0:
                    pages = [val]
            elif isinstance(val, str):
                val = val.strip()
                if "-" in val and "," not in val:
                    # 範圍格式：3-9 或 3-0（0=最後一頁）、0-0（全文件）
                    parts = val.split("-", 1)
                    if len(parts) == 2:
                        start_raw = parts[0].strip()
                        end_raw = parts[1].strip()
                        start = 1 if start_raw == "0" else int(start_raw)
                        end = total_pages if end_raw == "0" and total_pages > 0 else int(end_raw)
                        if end_raw == "0" and total_pages <= 0:
                            continue  # 無法解析「至最後一頁」，跳過此區塊
                        if start <= end and end > 0:
                            range_pages = list(range(start, end + 1))
                            step = skip + 1
                            pages = [range_pages[i] for i in range(0, len(range_pages), step)]
                else:
                    # 逗號分隔：1,3,5,7
                    pages = [int(x.strip()) for x in val.split(",") if x.strip()]
            elif isinstance(val, (list, tuple)):
                pages = [int(x) for x in val]

        if "page" in r:
            p = int(r["page"])
            if p > 0:
                pages.append(p)

        for p in pages:
            if p > 0:
                rotation_map[p - 1] = a  # 1-based -> 0-based

    return dict(sorted(rotation_map.items()))


def _get_rotated_page_rect(src_page: fitz.Page, angle: float) -> fitz.Rect:
    """取得旋轉後頁面的邊界矩形。90°、270° 時寬高對調。"""
    rect = src_page.rect
    angle_90 = round(angle % 360) if angle >= 0 else round((-angle) % 360)
    if angle_90 in (90, 270):
        return fitz.Rect(0, 0, rect.height, rect.width)
    return rect


def build_pdf_with_rotation(
    src_doc: fitz.Document,
    rotation_map: dict[int, float],
) -> fitz.Document:
    """
    依旋轉設定重建 PDF。非旋轉頁面用 insert_pdf 複製，旋轉頁面用 show_pdf_page 重建。

    Args:
        src_doc: 來源 PDF
        rotation_map: {page_index: angle}，0-based，已依頁碼排序

    Returns:
        新文件（需由呼叫者關閉）
    """
    total_pages = len(src_doc)
    if not rotation_map:
        return src_doc

    sorted_rotations = sorted(rotation_map.items())
    # 過濾超出範圍的頁碼
    valid_rotations = [(i, a) for i, a in sorted_rotations if 0 <= i < total_pages]
    for i, _ in sorted_rotations:
        if i < 0 or i >= total_pages:
            print(f"警告：旋轉頁碼 {i + 1} 超出範圍（共 {total_pages} 頁），跳過", file=sys.stderr)

    if not valid_rotations:
        return src_doc

    new_doc = fitz.open()
    first_rot = valid_rotations[0][0]
    last_rot = valid_rotations[-1][0]

    # 第一個旋轉頁面之前
    if first_rot > 0:
        new_doc.insert_pdf(src_doc, from_page=0, to_page=first_rot - 1)

    # 依序處理每個旋轉頁面及其之間的區段
    for idx, (rot_page, angle) in enumerate(valid_rotations):
        # 旋轉頁面：建立新頁面並 show_pdf_page
        src_page = src_doc[rot_page]
        rect = _get_rotated_page_rect(src_page, angle)
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        # 使用者：正值=順時針。PyMuPDF rotate 需實測，先取負值對應逆時針
        new_page.show_pdf_page(
            fitz.Rect(0, 0, rect.width, rect.height),
            src_doc,
            rot_page,
            rotate=-angle,
            keep_proportion=True,
        )

        # 此旋轉頁面與下一個旋轉頁面之間
        if idx + 1 < len(valid_rotations):
            next_rot = valid_rotations[idx + 1][0]
            if next_rot > rot_page + 1:
                new_doc.insert_pdf(
                    src_doc,
                    from_page=rot_page + 1,
                    to_page=next_rot - 1,
                )

    # 最後一個旋轉頁面之後
    if last_rot < total_pages - 1:
        new_doc.insert_pdf(
            src_doc,
            from_page=last_rot + 1,
            to_page=total_pages - 1,
        )

    return new_doc


def _apply_crop(
    doc: fitz.Document,
    margins: dict[str, float],
    start_page: int,
    end_page: int,
) -> None:
    """對文件套用裁切設定。"""
    left = margins.get("left", 0)
    right = margins.get("right", 0)
    top = margins.get("top", 0)
    bottom = margins.get("bottom", 0)

    total_pages = len(doc)
    start_index = (start_page - 1) if start_page > 0 else 0
    end_index = (total_pages - 2) if end_page == -1 else (total_pages - 1)

    for page_num in range(total_pages):
        if page_num < start_index or page_num > end_index:
            continue

        page = doc[page_num]
        rect = page.rect

        crop_rect = fitz.Rect(
            left,
            top,
            rect.width - right,
            rect.height - bottom,
        )

        if crop_rect.width <= 0 or crop_rect.height <= 0:
            print(
                f"警告：第 {page_num + 1} 頁裁切區域無效，跳過裁切",
                file=sys.stderr,
            )
            continue

        page.set_cropbox(crop_rect)


def crop_pdf(
    input_path: Path,
    output_path: Path,
    margins: dict[str, float],
    start_page: int = 2,
    end_page: int = 0,
    rotation_list: list[dict] | None = None,
) -> None:
    """
    裁切 PDF 留白區域，可選套用頁面旋轉。

    處理流程：先開啟 PDF 取得總頁數，若 pages 含 "3-0" 則在記憶體中解析為
    3 至最後一頁，再進行旋轉與裁切。不修改 config 檔案。

    Args:
        input_path: 輸入 PDF 路徑
        output_path: 輸出 PDF 路徑
        margins: 留白裁切量 dict，包含 left, right, top, bottom（單位：點）
        start_page: 開始裁切頁數（1-based），0或1=封面也裁切，2=封面不裁切
        end_page: 結束裁切頁數，0=裁切到最後一頁，-1=最後一頁不裁切
        rotation_list: [[rotation]] 設定，每筆含 page 或 pages（1-based）、angle
    """
    src_doc = fitz.open(input_path)
    doc: fitz.Document | None = None

    try:
        if rotation_list:
            total_pages = len(src_doc)
            rotation_map = _parse_rotation_list(rotation_list, total_pages)
            doc = build_pdf_with_rotation(src_doc, rotation_map)
            src_doc.close()
            src_doc = None
        else:
            doc = src_doc
            src_doc = None

        _apply_crop(doc, margins, start_page, end_page)
        doc.save(output_path, garbage=1, deflate=True)
    finally:
        if src_doc is not None:
            src_doc.close()
        if doc is not None:
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
    rotation_list = config.get("rotation", [])

    print(f"留白設定：左 {margins.get('left', 0)}pt, 右 {margins.get('right', 0)}pt, "
          f"上 {margins.get('top', 0)}pt, 下 {margins.get('bottom', 0)}pt")
    print(f"頁數範圍：從第 {start_page} 頁開始，"
          f"{'至最後一頁' if end_page == 0 else '最後一頁不裁切'}")
    if rotation_list:
        print(f"旋轉頁面：{_format_rotation_display(rotation_list)}")

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
            crop_pdf(input_path, output_path, margins, start_page, end_page, rotation_list)
            save_config_to_output(args.config.resolve(), output_path)
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

        _safe_print(f"裁切中：{args.input} -> {output_path}")
        crop_pdf(args.input, output_path, margins, start_page, end_page, rotation_list)
        save_config_to_output(args.config.resolve(), output_path)
        print("完成！")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
