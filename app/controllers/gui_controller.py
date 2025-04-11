def launch_gui(config_path=None, input_path=None, output_path=None, workers=5):
    """
    Lancement de l'interface graphique.

    :param config_path: Chemin vers un fichier de configuration (optionnel)
    :param input_path: Répertoire PDF par défaut (optionnel)
    :param output_path: Fichier de sortie par défaut (optionnel)
    :param workers: Nombre de threads par défaut
    """
    print("[GUI] Lancement de l'interface graphique...")
    print(f"→ Config: {config_path}, Input: {input_path}, Output: {output_path}, Workers: {workers}")

    import tkinter as tk

    root = tk.Tk()
    root.title("GeniePDF - Interface Graphique")
    tk.Label(root, text="GUI à implémenter ici avec les paramètres chargés").pack(padx=20, pady=20)
    root.mainloop()
