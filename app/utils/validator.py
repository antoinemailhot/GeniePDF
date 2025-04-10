import jsonschema
from jsonschema import validate

# Schéma d'exemple à adapter selon ta structure
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "champ1": {"type": "string"},
            "champ2": {"type": "number"},
            # ... ajouter ici d'autres champs
        },
        "required": ["champ1", "champ2"]
    }
}

def validate_json(data):
    """
    Valide les données extraites contre un schéma JSON prédéfini.

    :param data: Données (souvent liste de dicts) à valider.
    :return: True si la validation est réussie, False sinon.
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Erreur de validation JSON: {e.message}")
        return False
