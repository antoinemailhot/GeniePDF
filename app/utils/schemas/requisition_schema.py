schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "identifiant": {"type": "string"},
            "localisation": {"type": "string"},
            "statut": {"type": "string"},
            "diametre": {"type": "number"},
            "hauteur": {"type": "number"},
            "materiau": {"type": "string"}
        },
        "required": ["identifiant", "statut", "diametre"]
    }
}