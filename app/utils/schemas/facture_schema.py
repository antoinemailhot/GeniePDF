schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "numero_facture": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "montant": {"type": "number"},
            "client": {"type": "string"},
            "devise": {"type": "string"}
        },
        "required": ["numero_facture", "date", "montant", "client"]
    }
}