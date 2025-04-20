# data_structuring/pandas_processor.py
import pandas as pd
from collections.abc import Mapping

def structurize(raw_pages, file_path):
    """
    Transforme raw_pages (liste par page) en :
      1) DataFrame "long" (une ligne = 1 modèle extrait)
      2) liste de dicts {"file":..., "pages":[…]}   — groupé par fichier
    """
    # ---------- 1. Collecte des enregistrements ----------
    recs = []
    for p_idx, page in enumerate(raw_pages, start=1):
        if not page:                          # page OCR sans rien d'utile
            continue
        for model in page:
            if not isinstance(model, Mapping):
                # skip éléments non‑dict (None, [], NaN, etc.)
                continue
            item = model.copy()
            item["file"] = file_path
            item["page"] = p_idx
            recs.append(item)

    if not recs:            # Aucun modèle trouvé dans tout le PDF
        return pd.DataFrame(), [{"file": file_path, "pages": []}]

    # ---------- 2. DataFrame long ----------
    df = pd.json_normalize(recs, sep="_")
    df = df.dropna(axis=1, how="all")  # supprime colonnes entièrement vides
    payload_cols = df.columns.difference(["file", "page", "model"])
    df = df.dropna(how="all", subset=payload_cols)

    # page en int, mais uniquement si elle existe et sans NaN
    if "page" in df.columns:
        df["page"] = df["page"].astype("Int64")   # type nullable

    # ---------- 3. Regroupement par fichier ----------
    # plus rapide et plus stable que .apply(lambda …)
    grouped = (
        df.sort_values(["file", "page"])
          .groupby("file", sort=False, as_index=False)
          .agg(pages=("model",  # 'model' juste pour compter, on remplace après
                       lambda _: []))        # placeholder
          .to_dict(orient="records")
    )

    # On remplit réellement la clé "pages"
    pages_per_file = (
        df.sort_values(["file", "page"])
          .groupby("file", sort=False)
          .apply(lambda g: g.to_dict(orient="records"))
    )
    for d in grouped:
        d["pages"] = pages_per_file[d["file"]]

    return df.reset_index(drop=True), grouped
