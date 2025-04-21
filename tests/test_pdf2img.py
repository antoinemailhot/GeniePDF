import os
import pytest
from src.pdf_tools import pdf2image_wrapper as pw

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        pw.convert_pdf_to_images("not_here.pdf")

def test_convert_ok(monkeypatch_pdf, tmp_path):
    # Fichier bidon
    pdf = tmp_path / "dummy.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%EOF")
    pages = pw.convert_pdf_to_images(pdf)
    assert len(pages) == 2
