
import re
from datetime import datetime

def extract_data_with_regex(text):
    """
    Détermine dynamiquement le type de document et applique l'extraction adaptée.
    Retourne un dictionnaire correspondant à l'un des modèles finaux : Piece, Tool, Customer, Profile, Requisition.
    """
    if "DIE ORDER FORM" in text.upper() or "DIE / TOOL PURCHASE ORDER" in text.upper():
        return {
            "requisition": extract_requisition(text)
        }
    elif "PIECE" in text.upper():
        return {
            "piece": extract_piece(text)
        }
    elif "TOOL" in text.upper():
        return {
            "tool": extract_tool(text)
        }
    elif "PROFILE" in text.upper():
        return {
            "profile": extract_profile(text)
        }
    elif "CUSTOMER" in text.upper():
        return {
            "customer": extract_customer(text)
        }
    else:
        return {}

def extract_requisition(text):
    requisition = {}
    requisition["requisitionStatus"] = _search(text, r"(requisition status|status)\s*[:\-]?\s*(\w+)", 2)
    requisition["description"] = _search(text, r"(description)\s*[:\-]?\s*(.+)", 2)
    requisition["receptionDate"] = _search(text, r"(reception date|delivery date)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", 2)
    requisition["customerPurchaseNumber"] = _search(text, r"(PO Number|purchase number|customer order)\s*[:\-]?\s*(\w+)", 2)
    requisition["contact"] = _search(text, r"(contact|die maker)\s*[:\-]?\s*(\w+)", 2)
    requisition["toolNumber"] = _search(text, r"tool number\s*[:\-]?\s*(\w+)", 1)
    requisition["cavityQuantity"] = _int(_search(text, r"cavities\s*[:\-]?\s*(\d+)", 1))
    requisition["doubleLayout"] = _bool("double layout" in text.lower())
    return requisition

def extract_piece(text):
    return {
        "copyNumber": _int(_search(text, r"copy number\s*[:\-]?\s*(\d+)", 1)),
        "location": _search(text, r"location\s*[:\-]?\s*(\w+)", 1),
        "status": _search(text, r"status\s*[:\-]?\s*(\w+)", 1),
        "type": _search(text, r"type\s*[:\-]?\s*(\w+)", 1),
        "diameter": _float(_search(text, r"diameter\s*[:\-]?\s*([\d.]+)", 1)),
        "height": _float(_search(text, r"height\s*[:\-]?\s*([\d.]+)", 1)),
        "nitrogen": _bool("nitride" in text.lower()),
        "surfaceNitrogen": _bool("surface nitrogen" in text.lower()),
        "toBeManufactured": _bool("to be manufactured" in text.lower()),
        "customerCode": _search(text, r"customer code\s*[:\-]?\s*(\w+)", 1)
    }

def extract_tool(text):
    return {
        "assemblyType": _search(text, r"(assembly type|die style)\s*[:\-]?\s*(\w+)", 2),
        "pressList": _search(text, r"press\s*[:\-]?\s*([\w\- ,]+)", 1),
        "canBeInterlock": _bool("interlock" in text.lower()),
        "description": _search(text, r"description\s*[:\-]?\s*(.+)", 1),
        "displayCode": _search(text, r"display code\s*[:\-]?\s*(\w+)", 1),
        "customerCode": _search(text, r"customer code\s*[:\-]?\s*(\w+)", 1),
        "totalStack": _float(_search(text, r"total stack\s*[:\-]?\s*([\d.]+)", 1)),
        "copyNumber": _int(_search(text, r"copy number\s*[:\-]?\s*(\d+)", 1))
    }

def extract_profile(text):
    return {
        "customerCodePrefix": _search(text, r"customer code prefix\s*[:\-]?\s*(\w+)", 1),
        "customerCode": _search(text, r"customer code\s*[:\-]?\s*(\w+)", 1),
        "description": _search(text, r"description\s*[:\-]?\s*(.+)", 1),
        "creationDate": _search(text, r"(creation date|date)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", 2),
        "alloy": _search(text, r"alloy\s*[:\-]?\s*(\w+)", 1),
        "mandrelQuantity": _int(_search(text, r"mandrel quantity\s*[:\-]?\s*(\d+)", 1)),
        "cavityQuantity": _int(_search(text, r"cavity quantity\s*[:\-]?\s*(\d+)", 1)),
        "interlock": _bool("interlock" in text.lower()),
        "zsc": _float(_search(text, r"zsc\s*[:\-]?\s*([\d.]+)", 1)),
        "doubleLayoutAngle": _float(_search(text, r"double layout angle\s*[:\-]?\s*([\d.]+)", 1)),
        "hasElectrode": _bool("electrode" in text.lower()),
        "hasMicrofinish": _bool("microfinish" in text.lower())
    }

def extract_customer(text):
    return {
        "nickname": _search(text, r"nickname\s*[:\-]?\s*(\w+)", 1),
        "phone": _search(text, r"phone\s*[:\-]?\s*(\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4})", 1),
        "billingAddress": _search(text, r"billing address\s*[:\-]?\s*(.+)", 1),
        "shippingAddress": _search(text, r"shipping address\s*[:\-]?\s*(.+)", 1),
        "companyName": _search(text, r"company name\s*[:\-]?\s*(.+)", 1)
    }

# Helpers
def _search(text, pattern, group=1):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else None

def _bool(val):
    return val if isinstance(val, bool) else str(val).lower() in ("yes", "true", "1")

def _int(val):
    try:
        return int(val)
    except:
        return None

def _float(val):
    try:
        return float(val)
    except:
        return None