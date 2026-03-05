"""端對端整合測試"""

from __future__ import annotations

import subprocess
import sys

import fitz

from ebook_crop.config import load_config
from ebook_crop.crop import crop_pdf


class TestEndToEnd:
    """端對端：載入設定、裁切 PDF、驗證輸出"""

    def test_basic_workflow(self, basic_5page_pdf, basic_config_path, output_dir):
        """基本流程：載入設定 -> 裁切 -> 驗證"""
        cfg = load_config(basic_config_path)
        margins = cfg["margins"]
        start_page = cfg["pages"]["start"]
        end_page = cfg["pages"]["end"]

        output = output_dir / "integration_basic.pdf"
        crop_pdf(basic_5page_pdf, output, margins, start_page, end_page)

        assert output.exists()
        doc = fitz.open(output)
        assert len(doc) == 5

        # 封面不裁切（start=2）
        assert abs(doc[0].cropbox.x0 - 0) < 0.1

        # 第 2-5 頁有裁切
        for i in range(1, 5):
            cb = doc[i].cropbox
            assert abs(cb.x0 - 36) < 0.1
            assert abs(cb.y0 - 36) < 0.1
        doc.close()

    def test_rotation_workflow(self, ten_pages_pdf, rotation_config_path, output_dir):
        """旋轉流程：載入含旋轉設定 -> 裁切 -> 驗證頁數與旋轉結果"""
        cfg = load_config(rotation_config_path)
        margins = cfg["margins"]
        start_page = cfg["pages"]["start"]
        end_page = cfg["pages"]["end"]
        rotation_list = cfg.get("rotation", [])

        output = output_dir / "integration_rotation.pdf"
        crop_pdf(ten_pages_pdf, output, margins, start_page, end_page, rotation_list)

        assert output.exists()
        doc = fitz.open(output)
        assert len(doc) == 10
        doc.close()

    def test_units_workflow(self, basic_5page_pdf, units_config_path, output_dir):
        """單位轉換流程：載入含單位設定 -> 裁切 -> 驗證"""
        cfg = load_config(units_config_path)
        margins = cfg["margins"]

        output = output_dir / "integration_units.pdf"
        crop_pdf(basic_5page_pdf, output, margins, start_page=1, end_page=0)

        assert output.exists()
        doc = fitz.open(output)
        cb = doc[0].cropbox
        # left = 1cm ≈ 28.35pt
        assert abs(cb.x0 - 72.0 / 2.54) < 0.5
        doc.close()

    def test_zero_margins_workflow(self, basic_5page_pdf, zero_margins_config_path, output_dir):
        """零留白流程：裁切量為零，頁面不變"""
        cfg = load_config(zero_margins_config_path)
        margins = cfg["margins"]

        output = output_dir / "integration_zero.pdf"
        crop_pdf(basic_5page_pdf, output, margins, start_page=1, end_page=0)

        assert output.exists()
        doc = fitz.open(output)
        cb = doc[0].cropbox
        assert abs(cb.x0 - 0) < 0.1
        assert abs(cb.y0 - 0) < 0.1
        doc.close()


class TestCliIntegration:
    """CLI 命令列整合測試"""

    def test_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main", "--version"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "ebook-crop" in result.stdout

    def test_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0

    def test_dry_run_single(self, basic_5page_pdf, basic_config_path):
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             str(basic_5page_pdf), "-c", str(basic_config_path), "--dry-run"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0

    def test_single_file_mode(self, basic_5page_pdf, basic_config_path, tmp_path):
        output = tmp_path / "cli_output.pdf"
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             str(basic_5page_pdf), "-o", str(output), "-c", str(basic_config_path)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert output.exists()

    def test_quiet_mode(self, basic_5page_pdf, basic_config_path, tmp_path):
        output = tmp_path / "cli_quiet.pdf"
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             str(basic_5page_pdf), "-o", str(output),
             "-c", str(basic_config_path), "-q"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        # 靜默模式 stdout 應較少輸出
        assert output.exists()

    def test_verbose_mode(self, basic_5page_pdf, basic_config_path, tmp_path):
        output = tmp_path / "cli_verbose.pdf"
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             str(basic_5page_pdf), "-o", str(output),
             "-c", str(basic_config_path), "-v"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert output.exists()

    def test_missing_input_file(self, basic_config_path):
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             "nonexistent.pdf", "-c", str(basic_config_path)],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_vq_conflict(self, basic_5page_pdf, basic_config_path):
        result = subprocess.run(
            [sys.executable, "-m", "ebook_crop.main",
             str(basic_5page_pdf), "-c", str(basic_config_path), "-v", "-q"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
