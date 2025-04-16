schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "nom_fichier": {"type": "string"},
            "texte_extrait": {"type": "string"}
        },
        "required": ["nom_fichier"]
    }
}