"""pytest 共用 fixtures"""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

# 樣本與輸出目錄
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "test" / "input"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "test" / "output"


@pytest.fixture(scope="session", autouse=True)
def ensure_output_dir():
    """確保測試輸出目錄存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def sample_dir() -> Path:
    return SAMPLE_DIR


@pytest.fixture
def output_dir() -> Path:
    return OUTPUT_DIR


@pytest.fixture
def basic_5page_pdf() -> Path:
    return SAMPLE_DIR / "basic_5page.pdf"


@pytest.fixture
def single_page_pdf() -> Path:
    return SAMPLE_DIR / "single_page.pdf"


@pytest.fixture
def ten_pages_pdf() -> Path:
    return SAMPLE_DIR / "ten_pages.pdf"


@pytest.fixture
def landscape_pdf() -> Path:
    return SAMPLE_DIR / "landscape.pdf"


@pytest.fixture
def small_page_pdf() -> Path:
    return SAMPLE_DIR / "small_page.pdf"


@pytest.fixture
def basic_config_path() -> Path:
    return SAMPLE_DIR / "test_basic.toml"


@pytest.fixture
def rotation_config_path() -> Path:
    return SAMPLE_DIR / "test_rotation.toml"


@pytest.fixture
def units_config_path() -> Path:
    return SAMPLE_DIR / "test_units.toml"


@pytest.fixture
def zero_margins_config_path() -> Path:
    return SAMPLE_DIR / "test_zero_margins.toml"


@pytest.fixture
def tmp_pdf(tmp_path: Path) -> Path:
    """建立臨時 PDF 用於測試"""
    pdf_path = tmp_path / "temp.pdf"
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)
        page.insert_text((100, 400), f"Temp page {i + 1}", fontsize=12)
    doc.save(pdf_path)
    doc.close()
    return pdf_path
