"""rotation.py 單元測試"""

from __future__ import annotations

import fitz

from ebook_crop.rotation import _get_rotated_page_rect, build_pdf_with_rotation


class TestGetRotatedPageRect:
    def _make_page(self, width: float = 595, height: float = 842) -> fitz.Page:
        doc = fitz.open()
        page = doc.new_page(width=width, height=height)
        return page

    def test_no_rotation(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, 0)
        assert rect.width == 595
        assert rect.height == 842

    def test_90_degrees(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, 90)
        assert rect.width == 842
        assert rect.height == 595

    def test_180_degrees(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, 180)
        assert rect.width == 595
        assert rect.height == 842

    def test_270_degrees(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, 270)
        assert rect.width == 842
        assert rect.height == 595

    def test_negative_90(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, -90)
        assert rect.width == 842
        assert rect.height == 595

    def test_arbitrary_angle(self):
        page = self._make_page()
        rect = _get_rotated_page_rect(page, 45)
        assert rect.width == 595
        assert rect.height == 842

    def test_landscape_page_90(self):
        page = self._make_page(width=842, height=595)
        rect = _get_rotated_page_rect(page, 90)
        assert rect.width == 595
        assert rect.height == 842


class TestBuildPdfWithRotation:
    def test_no_rotation_map(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {})
        assert result is src
        assert len(result) == 5
        src.close()

    def test_single_page_rotation(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {2: 90.0})
        assert len(result) == 5
        # 旋轉頁面（第 3 頁，index 2）寬高應對調
        page = result[2]
        assert abs(page.rect.width - 842) < 1
        assert abs(page.rect.height - 595) < 1
        result.close()
        src.close()

    def test_multiple_rotations(self, ten_pages_pdf):
        src = fitz.open(ten_pages_pdf)
        rotation_map = {1: 90.0, 5: 270.0, 8: 90.0}
        result = build_pdf_with_rotation(src, rotation_map)
        assert len(result) == 10
        for idx in [1, 5, 8]:
            page = result[idx]
            assert abs(page.rect.width - 842) < 1
        result.close()
        src.close()

    def test_first_page_rotation(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {0: 90.0})
        assert len(result) == 5
        assert abs(result[0].rect.width - 842) < 1
        result.close()
        src.close()

    def test_last_page_rotation(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {4: 90.0})
        assert len(result) == 5
        assert abs(result[4].rect.width - 842) < 1
        result.close()
        src.close()

    def test_out_of_range_page(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {99: 90.0})
        assert result is src  # 無有效旋轉，回傳原始文件
        src.close()

    def test_arbitrary_angle(self, basic_5page_pdf):
        src = fitz.open(basic_5page_pdf)
        result = build_pdf_with_rotation(src, {2: 45.0})
        assert len(result) == 5
        # 非 90/270 度不對調寬高
        page = result[2]
        assert abs(page.rect.width - 595) < 1
        result.close()
        src.close()

    def test_all_pages_rotated(self):
        doc = fitz.open()
        for _ in range(3):
            doc.new_page(width=595, height=842)
        rotation_map = {0: 90.0, 1: 90.0, 2: 90.0}
        result = build_pdf_with_rotation(doc, rotation_map)
        assert len(result) == 3
        for i in range(3):
            assert abs(result[i].rect.width - 842) < 1
        result.close()
        doc.close()
