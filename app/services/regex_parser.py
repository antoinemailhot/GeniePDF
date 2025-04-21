# services/regex_parser.py  –– version 2025‑04‑20
import re
from typing import List, Dict, Any

FLAGS = re.I | re.S

# ─────────── constantes ───────────
_ASS_TYPES = r"DBF|DF|DB|BAFF|H2|H3"

# ─────────── helpers ───────────
def _match(txt: str, pat: str, grp: int = 1):
    m = re.search(pat, txt, FLAGS)
    return m.group(grp).strip() if m else None

def _b(x) -> bool: return str(x).lower() in {"yes", "true", "1", "y", "oui"}
def _i(x):          return int(x)   if str(x).isdigit() else None
def _f(x):          return float(x.replace(",", ".")) if x else None

# ─────────── PIECE ───────────
def _extract_piece(block: str) -> Dict[str, Any]:
    lower = block.lower()
    return {
        "copyNumber":       _i(_match(block, r"\bcopy\s*#?\s*[:\-]?\s*(\d{1,3})")),
        "location":         _match(block, r"\blocation\b\s*[:\-]?\s*([\w\-/]+)"),
        "status":           _match(block, r"\bstatus\b\s*[:\-]?\s*([\w\-]+)"),
        "type":             _match(block, r"\btype\b\s*[:\-]?\s*([\w\-]+)"),
        "diameter":         _f(_match(block, r"\bdiam(?:eter)?\b\s*[:\-]?\s*([\d.,]+)")),
        "height":           _f(_match(block, r"\bheight\b\s*[:\-]?\s*([\d.,]+)")),
        "nitrogen":         _b("nitride"            in lower),
        "surfaceNitrogen":  _b("surface nitrogen"   in lower),
        "toBeManufactured": _b("to be manufactured" in lower),
        "customerCode":     _match(block, r"\bcustomer code\b\s*[:\-]?\s*([\w\-]+)"),
    }

def extract_piece(txt: str) -> List[Dict[str, Any]]:
    # On considère qu’un “PIECE” est aussi décrit par “HOLE(S)”
    blocks = re.split(r"\bPIECE\b|\bHOLE\b", txt, flags=FLAGS)[1:]
    return [_extract_piece(b) for b in blocks if b.strip()]

# ─────────── TOOL ───────────
def _extract_tool(block: str, copy_hint: int | None = None) -> Dict[str, Any]:
    lower = block.lower()
    return {
        "assemblyType":  _match(block, fr"\b({_ASS_TYPES})\b"),
        "pressList":     _match(block, r"\bpress(?: list)?\s*[:\-]?\s*([\w ,&\-]+)"),
        "canBeInterlock": _b("interlock" in lower),
        "description":    _match(block, r"\bdescription\b\s*[:\-]?\s*(.+)"),
        "displayCode":    _match(block, r"\bdisplay code\b\s*[:\-]?\s*([\w\-]+)"),
        "customerCode":   _match(block, r"\bcustomer code\b\s*[:\-]?\s*([\w\-]+)"),
        "totalStack":     _f(_match(block, r"\btotal stack\b\s*[:\-]?\s*([\d.,]+)")),
        "copyNumber":     copy_hint or _i(_match(block, r"\bcopy\b\s*(\d{1,3})")),
    }

def extract_tool(txt: str) -> List[Dict[str, Any]]:
    """
    Recherche chaque bloc démarrant par « Copy <n> » (c’est ce qu’on voit
    dans les PDF Tower/Keymark/…).
    """
    out: list[dict] = []
    for m in re.finditer(r"\bCopy\s+(\d{1,3})\b.*?(?=\bCopy\s+\d{1,3}\b|$)",
                         txt, FLAGS):
        block, num = m.group(0), _i(m.group(1))
        d = _extract_tool(block, copy_hint=num)
        out.append(d)
    return out

# ─────────── CUSTOMER / PROFILE : inchangé (bonus : on accepte “Tel :”) ───────────
def _extract_customer(block: str) -> Dict[str, Any]:
    return {
        "nickname"      : _match(block, r"\bnick(?:name)?\b\s*[:\-]?\s*([\w\-]+)"),
        "phone"         : _match(block, r"\b(?:phone|tel)\b\s*[:\-]?\s*([\d ()\-.]+)"),
        "billingAddress": _match(block, r"\bbilling address\b\s*[:\-]?\s*(.+)"),
        "shippingAddress": _match(block, r"\bshipping address\b\s*[:\-]?\s*(.+)"),
        "companyName"   : _match(block, r"\bcompany name\b\s*[:\-]?\s*(.+)"),
    }

def extract_customer(txt: str) -> List[Dict[str, Any]]:
    blk = _match(txt, r"\bCUSTOMER\b(.+?)(?:\bPROFILE\b|\Z)", 1)
    return [_extract_customer(blk)] if blk else []

# Profile et Requisition : seules de légers ajustements (cavityQuantity…)
def extract_requisition(txt: str) -> Dict[str, Any]:
    return {
        "requisitionStatus": _match(txt, r"\bstatus\b\s*[:\-]?\s*([\w\-]+)"),
        "description":       _match(txt, r"(?s)\bnotes?\b\s*[:\-]?\s*(.+?)(?:\n{2,}|$)"),
        "receptionDate":     _match(txt, r"\b(date|order date)\b\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", 2),
        "customerPurchaseNumber": _match(txt, r"\bPO\s*Number\b\s*[:\-]?\s*(\w+)"),
        "contact":           _match(txt, r"\bcontact\b\s*[:\-]?\s*([\w ,]+)"),
        "toolNumber":        _match(txt, r"\btool(?: |#)?number\b\s*[:\-]?\s*([\w\-]+)"),
        "cavityQuantity":    _i(_match(txt, r"\b(?:hole|cavity|copies?)s?\b.*?(\d{1,3})")),
        "doubleLayout":      _b("double layout" in txt.lower()),
    }

# ─────────── routeur ───────────
def extract_data_with_regex(text: str) -> List[Dict[str, Any]]:
    res: list[dict] = []
    for d in extract_piece(text):    res.append({"model": "piece",    **d})
    for d in extract_tool(text):     res.append({"model": "tool",     **d})
    for d in extract_customer(text): res.append({"model": "customer", **d})
    # profile (optionnel) :
    for d in re.split(r"\bPROFILE\b", text, flags=FLAGS)[1:]:
        p = _match(d, r".+", 0)      # on garde tout le bloc
        if p: res.append({"model": "profile", **{ "description": p.strip() }})
    req = extract_requisition(text)
    if any(req.values()):            res.append({"model": "requisition", **req})
    return res
