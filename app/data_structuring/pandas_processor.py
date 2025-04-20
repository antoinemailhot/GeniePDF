# data_structuring/pandas_processor.py
import pandas as pd

def structurize(raw_pages, file_path):
    """
    Construit un DataFrame *long* et retourne AUSSI un “payload” groupé par fichier.
    """
    recs = []
    for p_idx, page in enumerate(raw_pages, start=1):
        for model in page:
            item = model.copy()
            item["file"]  = file_path
            item["page"]  = p_idx
            recs.append(item)

    df = pd.json_normalize(recs, sep="_")
    df = df.dropna(axis=1, how="all")           # vire colonnes vides
    df = df.dropna(how="all", subset=df.columns.difference(["file","page","model"]))
    df["page"] = df["page"].astype(int)

    # ---------- structure “collection” ----------
    grouped = (
        df.sort_values(["file","page"])
          .groupby("file", sort=False)           # garde ordre d'apparition
          .apply(lambda g: g.to_dict(orient="records"))
          .reset_index(name="pages")
          .to_dict(orient="records")
    )
    return df, grouped      # ➀ DataFrame plat, ➁ liste groupée
