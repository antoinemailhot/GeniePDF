# data_structuring/pandas_processor.py
import pandas as pd

def structurize(raw_pages, file_path=None):
    """
    raw_pages : liste (une entrée par page) de listes/dicts
    file_path : injecté par gui/CLI
    Retourne un DataFrame déjà *long* (tidy).
    """
    # 1. On a une liste [ page0_records, page1_records, ... ]
    records = []
    for idx, one_page in enumerate(raw_pages, start=1):
        for rec in one_page:                 # rec = {"model": "...", ...}
            rec = rec.copy()
            rec["page"] = idx
            records.append(rec)

    df = pd.json_normalize(records, sep="_")
    if file_path:
        df["file"] = file_path
    # 2. Virer les colonnes *entièrement* vides
    df = df.dropna(how="all", axis=1)
    # 3. Ne garder que les lignes où au moins un champ du modèle n'est pas null
    payload_cols = [c for c in df.columns if c not in ("file", "page", "model")]
    df = df.dropna(subset=payload_cols, how="all")
    return df.reset_index(drop=True)
