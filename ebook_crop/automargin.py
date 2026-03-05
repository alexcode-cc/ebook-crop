"""自動偵測頁面內容邊界，計算裁切留白"""

from __future__ import annotations

import fitz  # PyMuPDF


def detect_content_bbox(page: fitz.Page) -> fitz.Rect | None:
    """
    偵測單頁內容邊界，回傳包含所有文字與繪圖的最小矩形。

    透過 PyMuPDF 擷取文字區塊與繪圖路徑，合併計算內容邊界。
    若頁面無內容則回傳 None。
    """
    rects: list[fitz.Rect] = []

    # 文字區塊
    text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in text_dict.get("blocks", []):
        if block.get("type") == 0:  # text block
            bbox = block.get("bbox")
            if bbox:
                rects.append(fitz.Rect(bbox))

    # 繪圖路徑
    drawings = page.get_drawings()
    for d in drawings:
        if d.get("rect"):
            rects.append(fitz.Rect(d["rect"]))

    # 圖片
    for img in page.get_images(full=True):
        try:
            img_rects = page.get_image_rects(img[0])
            for r in img_rects:
                if r and not r.is_empty:
                    rects.append(r)
        except Exception:
            pass

    if not rects:
        return None

    # 合併所有矩形取最小包圍矩形
    result = rects[0]
    for r in rects[1:]:
        result |= r

    return result


def compute_auto_margins(
    page: fitz.Page,
    offsets: dict[str, float] | None = None,
) -> dict[str, float] | None:
    """
    計算單頁的自動裁切留白量。

    回傳 {"left": ..., "right": ..., "top": ..., "bottom": ...}（單位：點）。
    若無法偵測內容則回傳 None。

    Args:
        page: PDF 頁面
        offsets: 微調偏移量（正值=向內多裁、負值=向外少裁）
    """
    bbox = detect_content_bbox(page)
    if bbox is None:
        return None

    rect = page.rect
    off = offsets or {}
    off_left = off.get("left", 0)
    off_right = off.get("right", 0)
    off_top = off.get("top", 0)
    off_bottom = off.get("bottom", 0)

    left = max(0, bbox.x0 + off_left)
    top = max(0, bbox.y0 + off_top)
    right = max(0, rect.width - bbox.x1 + off_right)
    bottom = max(0, rect.height - bbox.y1 + off_bottom)

    return {"left": left, "right": right, "top": top, "bottom": bottom}


def apply_auto_crop(
    doc: fitz.Document,
    start_page: int,
    end_page: int,
    offsets: dict[str, float] | None = None,
) -> list[dict]:
    """
    對文件各頁自動偵測內容邊界並套用裁切。

    每頁獨立偵測，無法偵測的頁面跳過。

    Args:
        doc: PDF 文件
        start_page: 開始裁切頁數（1-based）
        end_page: 結束裁切頁數，0=至最後，-1=不含最後一頁
        offsets: 微調偏移量

    Returns:
        每頁偵測結果列表，每筆含 page（1-based）、margins 或 skipped 原因
    """
    import sys

    from ebook_crop.i18n import t

    total_pages = len(doc)
    start_index = (start_page - 1) if start_page > 0 else 0
    end_index = (total_pages - 2) if end_page == -1 else (total_pages - 1)
    results: list[dict] = []

    for page_num in range(total_pages):
        if page_num < start_index or page_num > end_index:
            continue

        page = doc[page_num]
        margins = compute_auto_margins(page, offsets)

        if margins is None:
            print(t("warn_no_content", page=page_num + 1), file=sys.stderr)
            results.append({"page": page_num + 1, "skipped": t("skip_no_content")})
            continue

        rect = page.rect
        crop_rect = fitz.Rect(
            margins["left"],
            margins["top"],
            rect.width - margins["right"],
            rect.height - margins["bottom"],
        )

        if crop_rect.width <= 0 or crop_rect.height <= 0:
            print(t("warn_auto_invalid_crop", page=page_num + 1), file=sys.stderr)
            results.append({"page": page_num + 1, "skipped": t("skip_invalid_crop")})
            continue

        page.set_cropbox(crop_rect)
        results.append({"page": page_num + 1, "margins": margins})

    return results
