import json
import pandas as pd
from src.gui_controller import launch_gui  # on testera process_data isolément
from src.gui_controller import process_data  # si vous l'avez exposée

def test_process_data(monkeypatch_pdf, monkeypatch_ocr, tmp_path):
    # Crée un faux PDF
    pdf = tmp_path / "file.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%EOF")
    df, collections = process_data([str(pdf)])
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert isinstance(collections, list) and collections  # au moins un élément
