import io
from PIL import Image
import pytest

@pytest.fixture
def dummy_images():
    # retourne 2 pages A4 blanches (RGB)
    return [Image.new("RGB", (595, 842), "white") for _ in range(2)]

@pytest.fixture
def monkeypatch_pdf(monkeypatch, dummy_images):
    # Intercepte pdf2image.convert_from_path
    import pdf2image
    monkeypatch.setattr(pdf2image, "convert_from_path",
                        lambda *a, **k: dummy_images)
    return monkeypatch

@pytest.fixture
def monkeypatch_ocr(monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract, "image_to_string",
                        lambda img, **k: "DUMMY TEXT")
    monkeypatch.setattr(pytesseract, "image_to_osd",
                        lambda img, **k: {"rotate": 0})
    return monkeypatch
