import os
import json
from genson import SchemaBuilder
from jsonschema import validate, ValidationError
from utils.schema_manager import get_schema, load_schemas, SCHEMA_DIR, get_schema

BACKUP_DIR = os.path.join(SCHEMA_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def validate_schema_with_examples(schema: dict, examples: list) -> bool:
    for item in examples:
        try:
            validate(instance=item, schema=schema)
        except ValidationError:
            return False
    return True

def save_schema(doc_type: str, schema_dict: dict):
    filename = f"{doc_type}_schema.py"
    path = os.path.join(SCHEMA_DIR, filename)
    backup_path = os.path.join(BACKUP_DIR, f"{doc_type}.bak.json")

    try:
        old_schema = get_schema(doc_type)
        if old_schema:
            with open(backup_path, "w") as f:
                json.dump(old_schema, f, indent=2)

        with open(path, "w") as f:
            f.write("schema = ")
            json.dump(schema_dict, f, indent=2)
            f.write("\n")

        print(f"✅ Schéma '{doc_type}' mis à jour.")
        load_schemas()

    except Exception as e:
        print(f"❌ Échec de sauvegarde du schéma '{doc_type}': {e}")

def update_schema_if_needed(doc_type: str, new_examples: list):
    if not new_examples:
        print(f"⚠️ Aucune donnée pour '{doc_type}'.")
        return

    builder = SchemaBuilder()
    for example in new_examples:
        builder.add_object(example)

    proposed_schema = builder.to_schema()

    if validate_schema_with_examples(proposed_schema, new_examples):
        save_schema(doc_type, proposed_schema)
    else:
        print(f"❌ Nouveau schéma invalide pour '{doc_type}' avec les exemples donnés.")

def update_schema_structure(doc_type: str, new_examples: list):
    update_schema_if_needed(doc_type, new_examples)
    print(f"✅ Mise à jour du schéma '{doc_type}' terminée.")