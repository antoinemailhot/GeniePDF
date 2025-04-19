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
from utils.schema_updater import update_schema_structure
from utils.schema_manager import load_schemas

def launch_gui(config_path=None, input_path=None, output_path=None, workers=5):
    selected_files = []
    config = load_config() if config_path is None else load_config(config_path)

    if input_path:
        if os.path.isdir(input_path):
            for root_dir, _, files in os.walk(input_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, f)
                        if full_path not in selected_files:
                            selected_files.append(full_path)
        elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            selected_files.append(input_path)

    root = tk.Tk()
    root.title("GeniePDF - Interface graphique")

    # ==== Interface graphique ====
    file_frame = ttk.LabelFrame(root, text="Fichiers PDF sélectionnés")
    file_frame.pack(fill="both", expand=True, padx=10, pady=5)

    file_listbox = tk.Listbox(file_frame, height=10)
    file_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0), pady=5)

    scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    file_listbox.config(yscrollcommand=scrollbar.set)

    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=5)

    def update_file_listbox():
        file_listbox.delete(0, tk.END)
        for f in selected_files:
            file_listbox.insert(tk.END, f)

    def add_pdf_file():
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
        if file_path and file_path not in selected_files:
            selected_files.append(file_path)
            update_file_listbox()

    def add_pdf_folder():
        folder_path = filedialog.askdirectory()
        if folder_path:
            for root_dir, _, files in os.walk(folder_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, f)
                        if full_path not in selected_files:
                            selected_files.append(full_path)
            update_file_listbox()

    def remove_selected_file():
        selected_indices = file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné pour suppression.")
            return
        for index in reversed(selected_indices):
            del selected_files[index]
        update_file_listbox()

    def choose_output():
        output = filedialog.asksaveasfilename(
            title="Choisissez le fichier de sortie",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json")]
        )
        if output:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, output)

    ttk.Button(button_frame, text="Ajouter un fichier PDF", command=add_pdf_file).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Ajouter un dossier", command=add_pdf_folder).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Supprimer sélection", command=remove_selected_file).pack(side=tk.LEFT)

    output_frame = ttk.Frame(root)
    output_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(output_frame, text="Fichier de sortie :").pack(side=tk.LEFT)
    output_entry = ttk.Entry(output_frame, width=50)
    output_entry.pack(side=tk.LEFT, padx=(5, 0))
    ttk.Button(output_frame, text="Parcourir", command=choose_output).pack(side=tk.LEFT)

    progress_label = ttk.Label(root, text="")
    progress_label.pack(pady=(0, 5))

    progress_bar = ttk.Progressbar(root, mode="indeterminate")
    progress_bar.pack(fill="x", padx=10, pady=(0, 5))

    start_button = ttk.Button(root, text="Démarrer", command=lambda: start_processing())
    start_button.pack(pady=5)

    def process_data(file_list):
        results = []
        for pdf_file in file_list:
            images = pdf2image_wrapper.convert_pdf_to_images(pdf_file)
            processed_images = [image_cleaner.preprocess(img) for img in images]
            texts = [tesseract_engine.extract_text(img) for img in processed_images]
            extracted_data = [extract_data_with_regex(text) for text in texts]
            df = pandas_processor.structurize(extracted_data)
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Résultat non DataFrame pour '{pdf_file}'")
            results.append(df)
        aggregated = aggregate_results(results)
        if not isinstance(aggregated, pd.DataFrame):
            aggregated = pd.concat(aggregated, ignore_index=True) if aggregated else pd.DataFrame()
        return aggregated

    def start_processing():
        chosen_output = output_entry.get()
        if not selected_files:
            messagebox.showwarning("Avertissement", "Aucun fichier PDF n'a été sélectionné.")
            return
        if not chosen_output:
            messagebox.showwarning("Avertissement", "Veuillez choisir un fichier de sortie.")
            return

        # Déterminer le type de document et les nouveaux exemples
        doc_type = "facture"  # Remplacez cela par le type de document approprié
        new_examples = [{"exemple_key": "exemple_value"}]  # Remplacez cela par les exemples appropriés

        # Mise à jour du schéma
        update_schema_structure(doc_type, new_examples)

        start_button.config(state=tk.DISABLED)
        progress_label.config(text="Traitement en cours...")
        progress_bar.start(10)

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        future = executor.submit(process_data, selected_files)

        def check_future():
            if future.done():
                progress_bar.stop()
                try:
                    result = future.result()
                    records = result.to_dict(orient="records")
                    json_ready_data = [r for r in records if r]
                    if not json_ready_data:
                        messagebox.showwarning("Aucun résultat", "Aucune donnée n'a pu être extraite.")
                    else:
                        with open(chosen_output, "w", encoding="utf-8") as f:
                            json.dump(json_ready_data, f, indent=2, ensure_ascii=False)
                        if validate_json(json_ready_data):
                            messagebox.showinfo("Succès", "Traitement terminé avec succès.")
                        else:
                            messagebox.showerror("Erreur", "Validation JSON échouée.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur pendant le traitement : {e}")
                finally:
                    start_button.config(state=tk.NORMAL)
                    progress_label.config(text="")
            else:
                root.after(100, check_future)

        check_future()


    update_file_listbox()
    root.mainloop()
