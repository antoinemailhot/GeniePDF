# services/regex_parser.py
import re
from datetime import datetime
from typing import List, Dict, Any

# ──────────────────── Helpers génériques ────────────────────
_re_flags = re.IGNORECASE | re.DOTALL    # utile pour les blocs multi‑lignes

def _search_one(txt: str, pat: str, grp: int = 1):
    m = re.search(pat, txt, _re_flags)
    return m.group(grp).strip() if m else None

def _bool(val):
    return bool(val) if isinstance(val, bool) else str(val).lower() in {"yes","true","1"}

def _int(val):
    try: return int(val)
    except (TypeError, ValueError): return None

def _float(val):
    try: return float(val.replace(",", "."))  # gère 12,5 ↔ 12.5
    except (AttributeError, ValueError): return None

# Découpe un texte sur le mot‑clé d’en‑tête (Piece, Tool, …)
def _split_on(keyword: str, txt: str) -> List[str]:
    # ex : r'\bPIECE\b' coupe avant chaque occurrence du mot
    parts = re.split(fr'\b{keyword}\b', txt, flags=_re_flags)
    # re.split() garde la partie avant la 1ʳᵉ occur ; on l’ignore
    return [p for p in parts[1:] if p.strip()]

# ──────────────────── Extracteurs « one » (un seul bloc) ────────────────────
def _extract_piece(block: str) -> Dict[str, Any]:
    return {
        "copyNumber": _int   (_search_one(block, r"copy number\s*[:\-]?\s*(\d+)")),
        "location":   _search_one(block, r"location\s*[:\-]?\s*([\w\-]+)"),
        "status":     _search_one(block, r"status\s*[:\-]?\s*([\w\-]+)"),
        "type":       _search_one(block, r"type\s*[:\-]?\s*([\w\-]+)"),
        "diameter":   _float (_search_one(block, r"diameter\s*[:\-]?\s*([\d.,]+)")),
        "height":     _float (_search_one(block, r"height\s*[:\-]?\s*([\d.,]+)")),
        "nitrogen":             _bool("nitrogen"           in block.lower()),
        "surfaceNitrogen":      _bool("surface nitrogen"   in block.lower()),
        "toBeManufactured":     _bool("to be manufactured" in block.lower()),
        "customerCode": _search_one(block, r"customer code\s*[:\-]?\s*([\w\-]+)")
    }

def _extract_tool(block: str) -> Dict[str, Any]:
    return {
        "assemblyType":  _search_one(block, r"(assembly type|die style)\s*[:\-]?\s*(\w+)"),
        "pressList":     _search_one(block, r"press\s*[:\-]?\s*([\w ,\-]+)"),
        "canBeInterlock": _bool("interlock" in block.lower()),
        "description":    _search_one(block, r"description\s*[:\-]?\s*(.+)"),
        "displayCode":    _search_one(block, r"display code\s*[:\-]?\s*(\w+)"),
        "customerCode":   _search_one(block, r"customer code\s*[:\-]?\s*(\w+)"),
        "totalStack":     _float(_search_one(block, r"total stack\s*[:\-]?\s*([\d.,]+)")),
        "copyNumber":     _int  (_search_one(block, r"copy number\s*[:\-]?\s*(\d+)"))
    }

def _extract_profile(block: str) -> Dict[str, Any]:
    return {
        "customerCodePrefix": _search_one(block, r"customer code prefix\s*[:\-]?\s*(\w+)"),
        "customerCode":       _search_one(block, r"customer code\s*[:\-]?\s*(\w+)"),
        "description":        _search_one(block, r"description\s*[:\-]?\s*(.+)"),
        "creationDate":       _search_one(block, r"(creation date|date)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", 2),
        "alloy":              _search_one(block, r"alloy\s*[:\-]?\s*(\w+)"),
        "mandrelQuantity":    _int  (_search_one(block, r"mandrel quantity\s*[:\-]?\s*(\d+)")),
        "interlock":          _bool("interlock" in block.lower()),
        "zsc":                _float(_search_one(block, r"zsc\s*[:\-]?\s*([\d.,]+)")),
        "doubleLayoutAngle":  _float(_search_one(block, r"double layout angle\s*[:\-]?\s*([\d.,]+)")),
        "hasElectrode":       _bool("electrode"  in block.lower()),
        "hasMicrofinish":     _bool("microfinish" in block.lower())
    }

# Requisition & PO restent (généralement) uniques par page → extraction simple
def extract_requisition(txt: str) -> Dict[str, Any]:
    return {
        "requisitionStatus":      _search_one(txt, r"(requisition status|statut)\s*[:\-]?\s*(\w+)"),
        "description":            _search_one(txt, r"\bdescription\b\s*[:\-]?\s*(.+)"),
        "receptionDate":          _search_one(txt, r"(reception|delivery) date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", 2),
        "customerPurchaseNumber": _search_one(txt, r"(PO number|purchase number)\s*[:\-]?\s*(\w+)"),
        "contact":                _search_one(txt, r"(contact|die maker)\s*[:\-]?\s*(\w+)"),
        "toolNumber":             _search_one(txt, r"tool number\s*[:\-]?\s*(\w+)"),
        "doubleLayout":           _bool("double layout" in txt.lower())
    }

def extract_po(txt: str) -> Dict[str, Any]:
    # inch/mm dimensions : 120 × 35 ou 120x35
    dims = re.search(r"(\d+(?:[.,]\d+)?)\s*[x×]\s*(\d+(?:[.,]\d+)?)", txt, _re_flags)
    return {
        "poNumber":  _search_one(txt, r"(PO\s*Number|Num[ée]ro de bon)\s*[:\-]?\s*(\S+)"),
        "orderDate": _search_one(txt, r"(Order\s*Date|Date\s+de\s+commande)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", 2),
        "vendor":    _search_one(txt, r"(Vendor|Fournisseur)\s*[:\-]?\s*(\S+)"),
        "partNumber": _search_one(txt, r"(MW[-−]\d+)"),
        "dimensions": {"width": _float(dims.group(1)), "height": _float(dims.group(2))} if dims else None,
        "unitPrice":  _float(_search_one(txt, r"(Unit Price|Prix Unitaire).*?([\d,]+\.\d+)")),
        "totalPrice": _float(_search_one(txt, r"(Total)\s*[:\-]?\s*([\d,]+\.\d+)"))
    }

# ──────────────────── Extracteurs « multi » ────────────────────
def extract_piece(txt: str) -> List[Dict[str, Any]]:
    return [_extract_piece(b) for b in _split_on("PIECE", txt)]

def extract_tool(txt: str) -> List[Dict[str, Any]]:
    return [_extract_tool(b) for b in _split_on("TOOL", txt)]

def extract_profile(txt: str) -> List[Dict[str, Any]]:
    return [_extract_profile(b) for b in _split_on("PROFILE", txt)]

def extract_customer(txt: str) -> List[Dict[str, Any]]:
    # pour l’instant : un seul customer par page
    bloc = _search_one(txt, r"\bCUSTOMER\b(.+?)(?:\bPROFILE\b|\Z)", 1)
    return [_extract_customer(bloc)] if bloc else []

def _extract_customer(block):  # helper privé
    return {
        "nickname":        _search_one(block, r"nickname\s*[:\-]?\s*(\w+)"),
        "phone":           _search_one(block, r"phone\s*[:\-]?\s*([\d ()\-\.]+)"),
        "billingAddress":  _search_one(block, r"billing address\s*[:\-]?\s*(.+)"),
        "shippingAddress": _search_one(block, r"shipping address\s*[:\-]?\s*(.+)"),
        "companyName":     _search_one(block, r"company name\s*[:\-]?\s*(.+)")
    }

# ──────────────────── Routeur principal ────────────────────
def extract_data_with_regex(text: str) -> List[Dict[str, Any]]:
    """
    Retourne une *liste* d’objets prêts à être transformés en JSON / DataFrame.
    Chaque élément contient :  
    • model   → 'piece' | 'tool' | …  
    • data    → le dict de champs  
    """
    results = []

    # Modèles possiblement multiples
    for d in extract_piece(text):    results.append({"model": "piece",    **d})
    for d in extract_tool(text):     results.append({"model": "tool",     **d})
    for d in extract_profile(text):  results.append({"model": "profile",  **d})
    for d in extract_customer(text): results.append({"model": "customer", **d})

    # Modèles uniques
    req = extract_requisition(text)
    if any(req.values()): results.append({"model": "requisition", **req})

    po  = extract_po(text)
    if any(po.values()):  results.append({"model": "po", **po})

    return results
