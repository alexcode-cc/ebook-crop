"""automargin.py 單元測試"""

from __future__ import annotations

import fitz

from ebook_crop.automargin import apply_auto_crop, compute_auto_margins, detect_content_bbox
from ebook_crop.config import load_config
from ebook_crop.crop import crop_pdf


class TestDetectContentBbox:
    def _make_page_with_text(
        self, width: float = 595, height: float = 842,
        x: float = 100, y: float = 200,
    ) -> fitz.Page:
        doc = fitz.open()
        page = doc.new_page(width=width, height=height)
        page.insert_text((x, y), "Hello World", fontsize=14, fontname="helv")
        return page

    def test_detects_text(self):
        page = self._make_page_with_text()
        bbox = detect_content_bbox(page)
        assert bbox is not None
        assert bbox.x0 > 0
        assert bbox.y0 > 0
        assert bbox.x1 < 595
        assert bbox.y1 < 842

    def test_text_position_affects_bbox(self):
        page1 = self._make_page_with_text(x=50, y=100)
        page2 = self._make_page_with_text(x=300, y=500)
        bbox1 = detect_content_bbox(page1)
        bbox2 = detect_content_bbox(page2)
        assert bbox1 is not None and bbox2 is not None
        assert bbox1.x0 < bbox2.x0
        assert bbox1.y0 < bbox2.y0

    def test_empty_page_returns_none(self):
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        bbox = detect_content_bbox(page)
        assert bbox is None

    def test_page_with_drawing(self):
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        shape = page.new_shape()
        shape.draw_rect(fitz.Rect(50, 50, 200, 200))
        shape.finish()
        shape.commit()
        bbox = detect_content_bbox(page)
        assert bbox is not None
        assert bbox.x0 <= 50
        assert bbox.y0 <= 50


class TestComputeAutoMargins:
    def _make_page_with_centered_text(self) -> fitz.Page:
        doc = fitz.open()
        page = doc.new_page(width=400, height=600)
        page.insert_text((100, 300), "Centered Text", fontsize=14, fontname="helv")
        return page

    def test_basic_margins(self):
        page = self._make_page_with_centered_text()
        margins = compute_auto_margins(page)
        assert margins is not None
        assert margins["left"] > 0
        assert margins["right"] > 0
        assert margins["top"] > 0
        assert margins["bottom"] > 0

    def test_offsets_increase_margins(self):
        page = self._make_page_with_centered_text()
        margins_no_offset = compute_auto_margins(page)
        margins_with_offset = compute_auto_margins(
            page, offsets={"left": 10, "right": 10, "top": 10, "bottom": 10}
        )
        assert margins_no_offset is not None and margins_with_offset is not None
        assert margins_with_offset["left"] > margins_no_offset["left"]
        assert margins_with_offset["top"] > margins_no_offset["top"]

    def test_negative_offsets_decrease_margins(self):
        page = self._make_page_with_centered_text()
        margins_no_offset = compute_auto_margins(page)
        margins_with_offset = compute_auto_margins(
            page, offsets={"left": -10, "right": -10, "top": -10, "bottom": -10}
        )
        assert margins_no_offset is not None and margins_with_offset is not None
        assert margins_with_offset["left"] < margins_no_offset["left"]

    def test_empty_page_returns_none(self):
        doc = fitz.open()
        page = doc.new_page(width=400, height=600)
        assert compute_auto_margins(page) is None


class TestApplyAutoCrop:
    def test_auto_crop_applied(self):
        doc = fitz.open()
        for _ in range(3):
            page = doc.new_page(width=595, height=842)
            page.insert_text((100, 400), "Content here", fontsize=14, fontname="helv")

        apply_auto_crop(doc, start_page=1, end_page=0)

        for i in range(3):
            cb = doc[i].cropbox
            # cropbox 應比原始頁面小
            assert cb.width < 595
            assert cb.height < 842
        doc.close()

    def test_skip_cover(self):
        doc = fitz.open()
        for _ in range(3):
            page = doc.new_page(width=595, height=842)
            page.insert_text((100, 400), "Content", fontsize=14, fontname="helv")

        apply_auto_crop(doc, start_page=2, end_page=0)

        # 封面不裁切
        cb0 = doc[0].cropbox
        assert abs(cb0.width - 595) < 1

        # 第 2 頁有裁切
        cb1 = doc[1].cropbox
        assert cb1.width < 595
        doc.close()

    def test_empty_page_skipped(self):
        doc = fitz.open()
        doc.new_page(width=595, height=842)  # 空白頁
        page2 = doc.new_page(width=595, height=842)
        page2.insert_text((100, 400), "Content", fontsize=14, fontname="helv")

        apply_auto_crop(doc, start_page=1, end_page=0)

        # 空白頁不裁切
        cb0 = doc[0].cropbox
        assert abs(cb0.width - 595) < 1

        # 有內容的頁面裁切
        cb1 = doc[1].cropbox
        assert cb1.width < 595
        doc.close()

    def test_with_offsets(self):
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((100, 400), "Content", fontsize=14, fontname="helv")

        apply_auto_crop(doc, start_page=1, end_page=0,
                        offsets={"left": 5, "right": 5, "top": 5, "bottom": 5})

        cb = doc[0].cropbox
        assert cb.width < 595
        doc.close()


class TestCropPdfWithAutoMargins:
    def test_auto_margins_config(self, basic_5page_pdf, output_dir):
        output = output_dir / "auto_basic.pdf"
        crop_pdf(
            basic_5page_pdf, output,
            margins={},
            start_page=1, end_page=0,
            auto_margins={"offsets": {"left": 0, "right": 0, "top": 0, "bottom": 0}},
        )
        assert output.exists()
        doc = fitz.open(output)
        assert len(doc) == 5
        # 有文字的頁面應被裁切
        cb = doc[0].cropbox
        assert cb.width < 595 or cb.height < 842
        doc.close()

    def test_auto_margins_with_offset(self, basic_5page_pdf, output_dir):
        output = output_dir / "auto_offset.pdf"
        crop_pdf(
            basic_5page_pdf, output,
            margins={},
            start_page=1, end_page=0,
            auto_margins={"offsets": {"left": 10, "right": 10, "top": 10, "bottom": 10}},
        )
        assert output.exists()

    def test_auto_margins_via_config(self, basic_5page_pdf, sample_dir, output_dir):
        cfg = load_config(sample_dir / "test_auto_margins.toml")
        auto_margins = cfg.get("_auto_margins")
        assert auto_margins is not None

        output = output_dir / "auto_config.pdf"
        crop_pdf(
            basic_5page_pdf, output,
            margins=cfg.get("margins", {}),
            start_page=1, end_page=0,
            auto_margins=auto_margins,
        )
        assert output.exists()

    def test_auto_margins_disabled_uses_manual(self, basic_5page_pdf, sample_dir, output_dir):
        """auto_margins 未啟用時，使用手動 margins"""
        cfg = load_config(sample_dir / "test_basic.toml")
        auto_margins = cfg.get("_auto_margins")
        assert auto_margins is None  # 未設定 auto_margins

        output = output_dir / "auto_disabled.pdf"
        crop_pdf(
            basic_5page_pdf, output,
            margins=cfg["margins"],
            start_page=2, end_page=0,
            auto_margins=auto_margins,
        )
        doc = fitz.open(output)
        # 手動裁切：第 2 頁 left=36
        cb = doc[1].cropbox
        assert abs(cb.x0 - 36) < 0.1
        doc.close()
