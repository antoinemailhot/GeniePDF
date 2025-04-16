schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "numero_plan": {"type": "string"},
            "titre_plan": {"type": "string"},
            "auteur": {"type": "string"},
            "date_creation": {"type": "string"},
            "dimensions": {"type": "string"}
        },
        "required": ["numero_plan", "titre_plan"]
    }
}