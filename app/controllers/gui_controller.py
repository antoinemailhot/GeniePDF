# controllers/gui_controller.py

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import concurrent.futures

# Importer ici les fonctions de traitement et validation.
# Assure-toi que ces modules sont correctement implémentés.
from pdf_tools import pdf2image_wrapper, image_cleaner
from ocr import tesseract_engine
from services.regex_parser import extract_data_with_regex
from data_structuring.aggregator import aggregate_results
from data_structuring import pandas_processor
from utils.validator import validate_json
from repositories.pdf_repository import PdfRepository
from utils.config import load_config

def launch_gui(config_path=None, input_path=None, output_path=None, workers=5):
    """
    Lance l'interface graphique de GeniePDF.
    Permet de :
      - Sélectionner un fichier PDF ou un dossier (récursivement)
      - Supprimer des fichiers sélectionnés
      - Choisir un chemin de sortie pour l'export JSON
      - Lancer le traitement en arrière-plan (sans bloquer l'interface)
    
    Les paramètres passés (config_path, input_path, output_path, workers) préchargent les champs.
    """
    
    # Liste des fichiers PDF sélectionnés
    selected_files = []

    # Instance de configuration si besoin de créer le repository
    config = load_config() if config_path is None else load_config(config_path)

    # Mettre à jour la configuration avec input_path et output_path s'ils sont fournis
    if input_path:
        if os.path.isdir(input_path):
            # Ajouter tous les fichiers PDF du dossier
            for root_dir, _, files in os.walk(input_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, f)
                        if full_path not in selected_files:
                            selected_files.append(full_path)
        elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            selected_files.append(input_path)
            
    # Fonction qui met à jour la listbox des fichiers sélectionnés
    def update_file_listbox():
        file_listbox.delete(0, tk.END)
        for f in selected_files:
            file_listbox.insert(tk.END, f)
    
    # Fonction d'ajout d'un fichier PDF
    def add_pdf_file():
        file_path = filedialog.askopenfilename(
            title="Sélectionnez un fichier PDF",
            filetypes=[("Fichiers PDF", "*.pdf")]
        )
        if file_path and file_path not in selected_files:
            selected_files.append(file_path)
            update_file_listbox()
    
    # Fonction d'ajout d'un dossier contenant des PDF (récursivement)
    def add_pdf_folder():
        folder_path = filedialog.askdirectory(title="Sélectionnez un dossier")
        if folder_path:
            for root_dir, _, files in os.walk(folder_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, f)
                        if full_path not in selected_files:
                            selected_files.append(full_path)
            update_file_listbox()
    
    # Fonction de suppression du fichier sélectionné dans la liste
    def remove_selected_file():
        selected_indices = file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné pour suppression.")
            return
        for index in reversed(selected_indices):
            del selected_files[index]
        update_file_listbox()
    
    # Fonction pour choisir le chemin de sortie
    def choose_output():
        # Ici nous choisissons un fichier de sortie JSON
        output = filedialog.asksaveasfilename(
            title="Choisissez le fichier de sortie",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json")]
        )
        if output:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, output)
    
    # Fonction de traitement en arrière-plan (dans un thread séparé)
    def process_data(file_list):
        # Similaire au pipeline défini dans main_cli.py
        results = []
        for pdf_file in file_list:
            images = pdf2image_wrapper.convert_pdf_to_images(pdf_file)
            processed_images = [image_cleaner.preprocess(img) for img in images]
            texts = [tesseract_engine.extract_text(img) for img in processed_images]
            extracted_data = [extract_data_with_regex(text) for text in texts]
            structured_data = pandas_processor.structurize(extracted_data)
            results.append(structured_data)
        aggregated = aggregate_results(results)
        return aggregated

    # Fonction appelée lorsqu'on lance le traitement via le bouton
    def start_processing():
        chosen_output = output_entry.get()
        if not selected_files:
            messagebox.showwarning("Avertissement", "Aucun fichier PDF n'a été sélectionné.")
            return
        if not chosen_output:
            messagebox.showwarning("Avertissement", "Veuillez choisir un fichier de sortie.")
            return

        # Désactiver le bouton pour éviter les clics multiples
        start_button.config(state=tk.DISABLED)
        progress_label.config(text="Traitement en cours...")
        
        # Lancer le traitement en arrière-plan via un ThreadPoolExecutor
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        future = executor.submit(process_data, selected_files)

        # Fonction pour vérifier le résultat sans bloquer l'interface
        def check_future():
            if future.done():
                try:
                    result = future.result()
                    # Validation des données avec le patron "Validator" (taux de précision pres de 100%)
                    if validate_json(result):
                        # Sauvegarde via le repository (optionnel si tu veux intégrer directement)
                        repo = PdfRepository(config.pdf_input_directory)
                        repo.save_extracted_data(result, chosen_output)
                        messagebox.showinfo("Succès", "Le traitement a été effectué et les données ont été sauvegardées.")
                    else:
                        messagebox.showerror("Erreur", "Validation JSON échouée. Vérifiez vos données extraites.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Une erreur s'est produite lors du traitement : {e}")
                finally:
                    progress_label.config(text="")
                    start_button.config(state=tk.NORMAL)
                    executor.shutdown()
            else:
                # Rappel la vérification après 100 ms
                root.after(100, check_future)
        root.after(100, check_future)
    
    # Création de la fenêtre principale
    root = tk.Tk()
    root.title("GeniePDF - Interface Graphique")

    # Cadre pour les boutons d'ajout/suppression
    button_frame = ttk.Frame(root)
    button_frame.pack(padx=10, pady=10, fill=tk.X)
    ttk.Button(button_frame, text="Ajouter un fichier PDF", command=add_pdf_file).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Ajouter un dossier", command=add_pdf_folder).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Supprimer sélection", command=remove_selected_file).pack(side=tk.LEFT, padx=5)

    # Cadre avec une listbox pour afficher les fichiers sélectionnés
    list_frame = ttk.Frame(root)
    list_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
    scrollbar.config(command=file_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Cadre pour choisir le chemin de sortie
    output_frame = ttk.Frame(root)
    output_frame.pack(padx=10, pady=5, fill=tk.X)
    ttk.Label(output_frame, text="Fichier de sortie :").pack(side=tk.LEFT, padx=5)
    output_entry = ttk.Entry(output_frame, width=40)
    output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    ttk.Button(output_frame, text="Parcourir...", command=choose_output).pack(side=tk.LEFT, padx=5)

    # Bouton pour démarrer le traitement et label de progression
    start_button = ttk.Button(root, text="Démarrer le traitement", command=start_processing)
    start_button.pack(pady=10)
    progress_label = ttk.Label(root, text="")
    progress_label.pack()

    # Chargement des valeurs préchargées (si elles sont fournies en argument)
    if input_path and os.path.exists(input_path):
        if os.path.isdir(input_path):
            for root_dir, _, files in os.walk(input_path):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, f)
                        if full_path not in selected_files:
                            selected_files.append(full_path)
        elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            selected_files.append(input_path)
        update_file_listbox()
    if output_path:
        output_entry.insert(0, output_path)

    root.mainloop()
