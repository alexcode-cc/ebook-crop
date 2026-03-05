"""生成測試用樣本 PDF 至 tests/input/ 目錄"""

from __future__ import annotations

from pathlib import Path

import fitz

SAMPLE_DIR = Path(__file__).resolve().parent / "input"


def _insert_text(page: fitz.Page, text: str) -> None:
    """在頁面中央插入文字"""
    rect = page.rect
    page.insert_text(
        (rect.width / 2 - 50, rect.height / 2),
        text,
        fontsize=14,
        fontname="helv",
    )


def generate_basic_5page() -> None:
    """5 頁 A4 PDF，每頁含文字"""
    doc = fitz.open()
    for i in range(1, 6):
        page = doc.new_page(width=595, height=842)  # A4
        _insert_text(page, f"Page {i} of 5")
    doc.save(SAMPLE_DIR / "basic_5page.pdf", garbage=1, deflate=True)
    doc.close()


def generate_single_page() -> None:
    """單頁 PDF"""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    _insert_text(page, "Single Page Document")
    doc.save(SAMPLE_DIR / "single_page.pdf", garbage=1, deflate=True)
    doc.close()


def generate_ten_pages() -> None:
    """10 頁 PDF，用於旋轉與頁數範圍測試"""
    doc = fitz.open()
    for i in range(1, 11):
        page = doc.new_page(width=595, height=842)
        _insert_text(page, f"Page {i} of 10")
    doc.save(SAMPLE_DIR / "ten_pages.pdf", garbage=1, deflate=True)
    doc.close()


def generate_landscape() -> None:
    """橫向 PDF"""
    doc = fitz.open()
    page = doc.new_page(width=842, height=595)  # A4 landscape
    _insert_text(page, "Landscape Page")
    doc.save(SAMPLE_DIR / "landscape.pdf", garbage=1, deflate=True)
    doc.close()


def generate_small_page() -> None:
    """小頁面 PDF，用於測試裁切邊界"""
    doc = fitz.open()
    page = doc.new_page(width=100, height=100)
    _insert_text(page, "Small")
    doc.save(SAMPLE_DIR / "small_page.pdf", garbage=1, deflate=True)
    doc.close()


def generate_all() -> None:
    """生成所有樣本 PDF"""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    generate_basic_5page()
    generate_single_page()
    generate_ten_pages()
    generate_landscape()
    generate_small_page()
    print(f"已生成樣本 PDF 至 {SAMPLE_DIR}")


if __name__ == "__main__":
    generate_all()
