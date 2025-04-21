from src.ocr import tesseract_engine as ocr
from src.services.regex_parser import extract_data_with_regex

def test_ocr_pipeline(monkeypatch_pdf, monkeypatch_ocr, dummy_images):
    txt = ocr.extract_text(dummy_images[0])
    assert txt == "DUMMY TEXT"
    # injection dans le parser
    recs = extract_data_with_regex(txt)
    assert isinstance(recs, list)
