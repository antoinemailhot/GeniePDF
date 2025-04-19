import os
import json
from jsonschema import validate, ValidationError
from utils.schema_manager import get_schema, SCHEMA_MAP

def try_schema_validation(data: dict, schema: dict) -> bool:
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False

def detect_document_type_by_schema(data: dict) -> str:
    for doc_type, schema in SCHEMA_MAP.items():
        if doc_type == "default":
            continue
        if try_schema_validation(data, schema):
            return doc_type
    return "default"

def detect_document_type(file_path: str) -> str:
    filename = os.path.basename(file_path).lower()
    if "facture" in filename or "invoice" in filename:
        return "facture"
    elif "plan" in filename:
        return "plan"
    elif "order" in filename or "requisition" in filename:
        return "requisition"
    return "default"

def validate_json(data: dict, file_path: str = None) -> bool:
    doc_type = detect_document_type(file_path) if file_path else "default"
    detected = detect_document_type_by_schema(data)
    if detected != "default":
        doc_type = detected

    schema = get_schema(doc_type)

    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        error_log = {
            "fichier": file_path or "inconnu",
            "type_detecte": doc_type,
            "erreur": e.message,
            "chemin": list(e.absolute_path)
        }
        with open('validation_errors.log', 'a') as f:
            f.write(json.dumps(error_log, indent=2) + "\n")
        return False