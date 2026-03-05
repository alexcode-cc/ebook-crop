"""邊界條件測試"""

from __future__ import annotations

import fitz

from ebook_crop.config import parse_rotation_list, validate_config
from ebook_crop.crop import crop_pdf
from ebook_crop.rotation import build_pdf_with_rotation


class TestSinglePageEdgeCases:
    """單頁 PDF 邊界測試"""

    def test_crop_single_page(self, single_page_pdf, output_dir):
        output = output_dir / "edge_single.pdf"
        crop_pdf(single_page_pdf, output, {"left": 10, "right": 10, "top": 10, "bottom": 10},
                 start_page=1)
        doc = fitz.open(output)
        assert len(doc) == 1
        cb = doc[0].cropbox
        assert abs(cb.x0 - 10) < 0.1
        doc.close()

    def test_rotate_single_page(self, single_page_pdf):
        src = fitz.open(single_page_pdf)
        result = build_pdf_with_rotation(src, {0: 90.0})
        assert len(result) == 1
        assert abs(result[0].rect.width - 842) < 1
        result.close()
        src.close()

    def test_crop_skip_cover_single_page(self, single_page_pdf, output_dir):
        """單頁 PDF 且 start=2，等於不裁切任何頁面"""
        output = output_dir / "edge_single_skip.pdf"
        crop_pdf(single_page_pdf, output, {"left": 36, "right": 36, "top": 36, "bottom": 36},
                 start_page=2)
        doc = fitz.open(output)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 0) < 0.1  # 未被裁切
        doc.close()


class TestSmallPageEdgeCases:
    """小頁面邊界測試"""

    def test_margins_exceed_page(self, small_page_pdf, output_dir):
        """留白超過頁面尺寸"""
        output = output_dir / "edge_small_exceed.pdf"
        crop_pdf(small_page_pdf, output, {"left": 60, "right": 60, "top": 60, "bottom": 60})
        doc = fitz.open(output)
        assert len(doc) == 1
        # 裁切區域無效，cropbox 應保持原狀
        cb = doc[0].cropbox
        assert cb.width > 0
        doc.close()


class TestLandscapeEdgeCases:
    """橫向頁面測試"""

    def test_crop_landscape(self, landscape_pdf, output_dir):
        output = output_dir / "edge_landscape.pdf"
        crop_pdf(landscape_pdf, output, {"left": 20, "right": 20, "top": 20, "bottom": 20},
                 start_page=1)
        doc = fitz.open(output)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 20) < 0.1
        assert abs(cb.x1 - (842 - 20)) < 0.1
        doc.close()

    def test_rotate_landscape_90(self, landscape_pdf):
        src = fitz.open(landscape_pdf)
        result = build_pdf_with_rotation(src, {0: 90.0})
        page = result[0]
        # 橫向旋轉 90 度：842x595 -> 595x842
        assert abs(page.rect.width - 595) < 1
        assert abs(page.rect.height - 842) < 1
        result.close()
        src.close()


class TestLargeFileEdgeCases:
    """大頁數 PDF 測試"""

    def test_50_pages(self, output_dir):
        """50 頁 PDF 的裁切"""
        doc = fitz.open()
        for i in range(50):
            page = doc.new_page(width=595, height=842)
            page.insert_text((100, 400), f"Page {i + 1}", fontsize=12)

        tmp = output_dir / "edge_50pages_src.pdf"
        doc.save(tmp)
        doc.close()

        output = output_dir / "edge_50pages_out.pdf"
        crop_pdf(tmp, output, {"left": 30, "right": 30, "top": 30, "bottom": 30})

        result = fitz.open(output)
        assert len(result) == 50
        cb = result[25].cropbox
        assert abs(cb.x0 - 30) < 0.1
        result.close()

    def test_50_pages_with_rotation(self, output_dir):
        """50 頁 PDF 含旋轉"""
        doc = fitz.open()
        for i in range(50):
            doc.new_page(width=595, height=842)

        tmp = output_dir / "edge_50rot_src.pdf"
        doc.save(tmp)
        doc.close()

        rotation_list = [{"pages": "0-0", "skip": 1, "angle": 90}]
        output = output_dir / "edge_50rot_out.pdf"
        crop_pdf(tmp, output, {"left": 10, "right": 10, "top": 10, "bottom": 10},
                 start_page=1, end_page=0, rotation_list=rotation_list)

        result = fitz.open(output)
        assert len(result) == 50
        result.close()


class TestRotationEdgeCases:
    """旋轉邊界測試"""

    def test_consecutive_rotated_pages(self):
        doc = fitz.open()
        for _ in range(5):
            doc.new_page(width=595, height=842)
        result = build_pdf_with_rotation(doc, {0: 90.0, 1: 90.0, 2: 90.0})
        assert len(result) == 5
        for i in range(3):
            assert abs(result[i].rect.width - 842) < 1
        # 後兩頁不旋轉
        assert abs(result[3].rect.width - 595) < 1
        result.close()
        doc.close()

    def test_only_last_page_rotated(self):
        doc = fitz.open()
        for _ in range(5):
            doc.new_page(width=595, height=842)
        result = build_pdf_with_rotation(doc, {4: 90.0})
        assert len(result) == 5
        assert abs(result[4].rect.width - 842) < 1
        assert abs(result[0].rect.width - 595) < 1
        result.close()
        doc.close()

    def test_negative_angle(self):
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        result = build_pdf_with_rotation(doc, {0: -90.0})
        assert abs(result[0].rect.width - 842) < 1
        result.close()
        doc.close()

    def test_360_degrees(self):
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        result = build_pdf_with_rotation(doc, {0: 360.0})
        assert abs(result[0].rect.width - 595) < 1
        result.close()
        doc.close()


class TestConfigEdgeCases:
    """設定檔邊界測試"""

    def test_empty_rotation_list(self):
        assert parse_rotation_list([], total_pages=10) == {}

    def test_page_zero_in_rotation(self):
        """page=0 應被忽略（頁碼需 > 0）"""
        result = parse_rotation_list([{"page": 0, "angle": 90}])
        assert result == {}

    def test_page_exceeds_total(self):
        result = parse_rotation_list([{"page": 100, "angle": 90}], total_pages=10)
        assert 99 in result  # 解析成功但 build_pdf_with_rotation 會過濾

    def test_validate_empty_config(self):
        assert validate_config({}) == []

    def test_validate_pages_end_minus_one(self):
        cfg = {"pages": {"end": -1}}
        assert validate_config(cfg) == []
