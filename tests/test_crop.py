"""crop.py 單元測試"""

from __future__ import annotations

import fitz

from ebook_crop.crop import _apply_crop, crop_pdf


class TestApplyCrop:
    def _make_doc(self, pages: int = 3, width: float = 595, height: float = 842) -> fitz.Document:
        doc = fitz.open()
        for _ in range(pages):
            doc.new_page(width=width, height=height)
        return doc

    def test_basic_crop(self):
        doc = self._make_doc()
        margins = {"left": 36, "right": 36, "top": 36, "bottom": 36}
        _apply_crop(doc, margins, start_page=1, end_page=0)

        for i in range(3):
            cb = doc[i].cropbox
            assert abs(cb.x0 - 36) < 0.1
            assert abs(cb.y0 - 36) < 0.1
            assert abs(cb.x1 - (595 - 36)) < 0.1
            assert abs(cb.y1 - (842 - 36)) < 0.1
        doc.close()

    def test_skip_cover(self):
        doc = self._make_doc()
        margins = {"left": 36, "right": 36, "top": 36, "bottom": 36}
        _apply_crop(doc, margins, start_page=2, end_page=0)

        # 封面（第 1 頁）不裁切
        cb0 = doc[0].cropbox
        assert abs(cb0.x0 - 0) < 0.1
        assert abs(cb0.y0 - 0) < 0.1

        # 第 2 頁有裁切
        cb1 = doc[1].cropbox
        assert abs(cb1.x0 - 36) < 0.1
        doc.close()

    def test_skip_back_cover(self):
        doc = self._make_doc(pages=5)
        margins = {"left": 36, "right": 36, "top": 36, "bottom": 36}
        _apply_crop(doc, margins, start_page=1, end_page=-1)

        # 最後一頁不裁切
        cb_last = doc[4].cropbox
        assert abs(cb_last.x0 - 0) < 0.1

        # 倒數第二頁有裁切
        cb_prev = doc[3].cropbox
        assert abs(cb_prev.x0 - 36) < 0.1
        doc.close()

    def test_zero_margins(self):
        doc = self._make_doc()
        margins = {"left": 0, "right": 0, "top": 0, "bottom": 0}
        _apply_crop(doc, margins, start_page=1, end_page=0)

        cb = doc[0].cropbox
        assert abs(cb.x0 - 0) < 0.1
        assert abs(cb.x1 - 595) < 0.1
        doc.close()

    def test_large_margins_skip(self):
        """留白大於頁面尺寸時，跳過該頁裁切"""
        doc = self._make_doc(pages=1, width=100, height=100)
        margins = {"left": 60, "right": 60, "top": 60, "bottom": 60}
        _apply_crop(doc, margins, start_page=1, end_page=0)

        # 裁切區域無效，應保持原始 cropbox
        cb = doc[0].cropbox
        assert cb.width > 0
        doc.close()

    def test_missing_margin_keys(self):
        doc = self._make_doc()
        margins = {}  # 全部預設為 0
        _apply_crop(doc, margins, start_page=1, end_page=0)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 0) < 0.1
        doc.close()

    def test_single_page_doc(self):
        doc = self._make_doc(pages=1)
        margins = {"left": 10, "right": 10, "top": 10, "bottom": 10}
        _apply_crop(doc, margins, start_page=1, end_page=0)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 10) < 0.1
        doc.close()


class TestCropPdf:
    def test_basic_crop(self, basic_5page_pdf, output_dir):
        output = output_dir / "crop_basic.pdf"
        margins = {"left": 36, "right": 36, "top": 36, "bottom": 36}
        crop_pdf(basic_5page_pdf, output, margins, start_page=2, end_page=0)

        assert output.exists()
        doc = fitz.open(output)
        assert len(doc) == 5

        # 封面不裁切
        cb0 = doc[0].cropbox
        assert abs(cb0.x0 - 0) < 0.1

        # 第 2 頁有裁切
        cb1 = doc[1].cropbox
        assert abs(cb1.x0 - 36) < 0.1
        doc.close()

    def test_crop_with_rotation(self, ten_pages_pdf, output_dir):
        output = output_dir / "crop_rotation.pdf"
        margins = {"left": 20, "right": 20, "top": 20, "bottom": 20}
        rotation_list = [{"page": 3, "angle": 90}]
        crop_pdf(ten_pages_pdf, output, margins, start_page=1, end_page=0,
                 rotation_list=rotation_list)

        assert output.exists()
        doc = fitz.open(output)
        assert len(doc) == 10
        doc.close()

    def test_crop_no_rotation(self, basic_5page_pdf, output_dir):
        output = output_dir / "crop_no_rot.pdf"
        margins = {"left": 10, "right": 10, "top": 10, "bottom": 10}
        crop_pdf(basic_5page_pdf, output, margins, start_page=1, end_page=0)

        assert output.exists()
        doc = fitz.open(output)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 10) < 0.1
        doc.close()

    def test_output_file_created(self, single_page_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        crop_pdf(single_page_pdf, output, {"left": 5, "right": 5, "top": 5, "bottom": 5})
        assert output.exists()
        assert output.stat().st_size > 0
