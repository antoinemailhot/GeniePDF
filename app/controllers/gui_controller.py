import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import concurrent.futures
import pandas as pd

from pdf_tools import pdf2image_wrapper, image_cleaner
from ocr import tesseract_engine
from services.regex_parser import extract_data_with_regex
from data_structuring.aggregator import aggregate_results
from data_structuring import pandas_processor
from utils.validator import validate_json
from utils.config import load_config

def launch_gui(config_path=None, input_path=None, output_path=None, workers=5):
    selected_files = []
    config = load_config() if config_path is None else load_config(config_path)

    # Préchargement éventuel du chemin d'entrée
    if input_path:
        if os.path.isdir(input_path):
            for root_dir, _, files in os.walk(input_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        path = os.path.join(root_dir, f)
                        if path not in selected_files:
                            selected_files.append(path)
        elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            selected_files.append(input_path)

    root = tk.Tk()
    root.title("GeniePDF - Interface graphique")

    # --- Zone de sélection des fichiers ---
    file_frame = ttk.LabelFrame(root, text="Fichiers PDF sélectionnés")
    file_frame.pack(fill="both", expand=True, padx=10, pady=5)
    file_listbox = tk.Listbox(file_frame, height=10)
    file_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=(5,0), pady=5)
    scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    file_listbox.config(yscrollcommand=scrollbar.set)

    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=5)

    def update_listbox():
        file_listbox.delete(0, tk.END)
        for p in selected_files:
            file_listbox.insert(tk.END, p)

    def add_file():
        p = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if p and p not in selected_files:
            selected_files.append(p)
            update_listbox()

    def add_folder():
        d = filedialog.askdirectory()
        if d:
            for rd, _, fs in os.walk(d):
                for f in fs:
                    if f.lower().endswith(".pdf"):
                        full = os.path.join(rd, f)
                        if full not in selected_files:
                            selected_files.append(full)
            update_listbox()

    def remove_selected():
        for idx in reversed(file_listbox.curselection()):
            selected_files.pop(idx)
        update_listbox()

    ttk.Button(button_frame, text="Ajouter un fichier", command=add_file).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Ajouter un dossier", command=add_folder).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Supprimer sélection", command=remove_selected).pack(side=tk.LEFT)

    # --- Choix du fichier de sortie ---
    output_frame = ttk.Frame(root)
    output_frame.pack(fill="x", padx=10, pady=5)
    ttk.Label(output_frame, text="Fichier de sortie :").pack(side=tk.LEFT)
    output_entry = ttk.Entry(output_frame, width=50)
    output_entry.pack(side=tk.LEFT, padx=(5,0), fill="x", expand=True)
    def choose_output():
        out = filedialog.asksaveasfilename(defaultextension=".json",
                                           filetypes=[("JSON", "*.json")])
        if out:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, out)
    ttk.Button(output_frame, text="Parcourir…", command=choose_output).pack(side=tk.LEFT, padx=5)

    # --- Barre de progression & statut ---
    progress_label = ttk.Label(root, text="")
    progress_label.pack(pady=(5,0))
    progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
    progress_bar.pack(fill="x", padx=10, pady=(0,5))

    # --- Traitement en arrière‑plan ---
    def process_data(file_list):
        dfs = []
        total = len(file_list)
        for i, pdf in enumerate(file_list, 1):
            # mise à jour du progrès
            progress_bar['value'] = (i-1)/total*100
            root.update_idletasks()

            imgs = pdf2image_wrapper.convert_pdf_to_images(pdf)
            imgs = [image_cleaner.preprocess(img) for img in imgs]
            txts = [tesseract_engine.extract_text(im) for im in imgs]
            raws = [extract_data_with_regex(t) for t in txts]
            df = pandas_processor.structurize(raws)
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Le PDF « {pdf} » n’a pas renvoyé un DataFrame.")
            dfs.append(df)

        # agrégation
        ag = aggregate_results(dfs)
        # ==== PRÉ-NETTOYAGE OPTIMISÉ ====
        # s'assurer d'un DataFrame
        if isinstance(ag, list):
            ag = pd.concat(ag, ignore_index=True)
        elif not isinstance(ag, pd.DataFrame):
            ag = pd.DataFrame()
        # retirer lignes et colonnes vides
        ag = ag.dropna(how='all').dropna(axis=1, how='all')
        return ag

    def start():
        outp = output_entry.get().strip()
        if not selected_files:
            return messagebox.showwarning("Avertissement", "Aucun PDF sélectionné.")
        if not outp:
            return messagebox.showwarning("Avertissement", "Spécifiez un fichier de sortie.")
        start_button.config(state=tk.DISABLED)
        progress_label.config(text="Traitement…")
        progress_bar['value'] = 0

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        future = executor.submit(process_data, list(selected_files))

        def check():
            if future.done():
                try:
                    df = future.result()
                    progress_bar['value'] = 100
                    recs = df.to_dict(orient="records")
                    with open(outp, "w", encoding="utf-8") as f:
                        json.dump(recs, f, indent=2, ensure_ascii=False)
                    if validate_json(recs):
                        messagebox.showinfo("Succès", "Terminé avec succès ! 🎉")
                    else:
                        messagebox.showerror("Erreur", "Validation JSON échouée.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Pendant le traitement : {e}")
                finally:
                    start_button.config(state=tk.NORMAL)
                    progress_label.config(text="")
                    executor.shutdown()
            else:
                root.after(100, check)

        root.after(100, check)

    start_button = ttk.Button(root, text="Démarrer", command=start)
    start_button.pack(pady=5)

    update_listbox()
    root.mainloop()
