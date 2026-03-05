"""PDF 頁面旋轉"""

from __future__ import annotations

import sys

import fitz  # PyMuPDF


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
