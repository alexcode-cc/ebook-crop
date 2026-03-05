"""PDF 留白裁切"""

from __future__ import annotations

import sys
from pathlib import Path

import fitz  # PyMuPDF

from ebook_crop import config, rotation


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
            rotation_map = config.parse_rotation_list(rotation_list, total_pages)
            doc = rotation.build_pdf_with_rotation(src_doc, rotation_map)
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
