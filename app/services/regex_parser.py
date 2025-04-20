# services/regex_parser.py  ──────────────────────────────────────────────
import re
from typing import List, Dict, Any
FLAGS = re.I | re.S

# ─────────── Helpers ───────────
def _match(txt: str, pat: str, grp: int = 1):
    m = re.search(pat, txt, FLAGS)
    return m.group(grp).strip() if m else None

def _b(val) -> bool:
    return str(val).lower() in {"yes", "true", "1", "y", "oui"}

def _i(val):                 # int nullable
    try: return int(val)
    except (TypeError, ValueError): return None

def _f(val):                 # float nullable
    try: return float(val.replace(",", "."))
    except (AttributeError, ValueError): return None

def _split_on(keyword: str, txt: str) -> List[str]:
    """Découpe avant chaque mot‑clé : 'PIECE', 'TOOL', 'PROFILE'…"""
    parts = re.split(fr"\b{keyword}\b", txt, flags=FLAGS)
    return [p for p in parts[1:] if p.strip()]

# ─────────── PIECE ───────────
def _extract_piece(block: str) -> Dict[str, Any]:
    txt = block.lower()
    return {
        "copyNumber"        : _i(_match(block, r"\bcopy\s*#?\s*[:\-]?\s*(\d+)")),
        "location"          : _match(block, r"\blocation\b\s*[:\-]?\s*([\w\-\/]+)"),
        "status"            : _match(block, r"\bstatus\b\s*[:\-]?\s*([\w\-]+)"),
        "type"              : _match(block, r"\btype\b\s*[:\-]?\s*([\w\-]+)"),
        "diameter"          : _f(_match(block, r"\bdiam(?:eter)?\b\s*[:\-]?\s*([\d.,]+)")),
        "height"            : _f(_match(block, r"\bheight\b\s*[:\-]?\s*([\d.,]+)")),
        "nitrogen"          : _b("nitrogen" in txt),
        "surfaceNitrogen"   : _b("surface nitrogen" in txt),
        "toBeManufactured"  : _b("to be manufactured" in txt),
        "customerCode"      : _match(block, r"\bcustomer code\b\s*[:\-]?\s*([\w\-]+)")
    }

def extract_piece(text: str) -> List[Dict[str, Any]]:
    return [_extract_piece(b) for b in _split_on("PIECE", text)]

# TOOL  ───────────────────────────────
def _extract_tool(block: str) -> Dict[str, Any]:
    txt = block.lower()



    # Copy dans la colonne tableau «  Copy »
    copy = _match(block, r"\bcopy\b\s*(\d{1,3})")          # ← 4
    if not copy:                                           # fallback “Copy #”
        copy = _match(block, r"\bcopy\s*#?\s*[:\-]?\s*(\d+)")

    return {
        "assemblyType"  : _match(block, fr"\b({ _ASS_TYPES })\b"),  # 8" Baff, DBF…
        "pressList"     : _match(block, r"\bpress\s*#?\s*[:\-]?\s*([\d, &]+)"), # « Press # 8 »
        "canBeInterlock": _b("interlock" in txt),
        "description"   : _match(block, r"\bdescription\b\s*[:\-]?\s*(.+)"),
        "displayCode"   : _match(block, r"\bdisplay code\b\s*[:\-]?\s*([\w\-]+)"),
        "customerCode"  : _match(block, r"\bcustomer code\b\s*[:\-]?\s*([\w\-]+)"),
        "totalStack"    : _f(_match(block, r"\btotal stack\b\s*[:\-]?\s*([\d.,]+)")),
        "copyNumber"    : _i(copy)
    }
# valeurs autorisées pour Assembly Type
_ASS_TYPES = r"DBF|DF|DB|BAFF|H2|H3"

def extract_tool(text: str) -> List[Dict[str, Any]]:
    """
    Découpe la zone tableau 'Die / Feeder / Backer / Bolster' OU
    – à défaut – chaque occurrence du mot 'TOOL', puis applique _extract_tool.
    Retourne une liste (possiblement vide) d'outils trouvés dans la page.
    """
    blocs = []

    # 1. Découpage spécifique Tower : lignes commençant par Die / Feeder / Backer / Bolster
    #    → cela évite de capturer le titre « DIE / TOOL PURCHASE ORDER ».
    rows = re.split(r"\b(Die|Feeder|Backer|Bolster)\b", text, flags=FLAGS)
    if len(rows) > 1:                      # on a bien trouvé le tableau
        i = 1                              # rows[0] = avant 1ʳᵉ occurrence, on saute
        while i < len(rows):
            payload = rows[i+1]            # le texte qui suit le mot‑clé
            blocs.append(payload)
            i += 2
    else:
        # 2. Fallback : on découpe simplement sur le mot 'TOOL'
        blocs = _split_on("TOOL", text)

    # 3. Extraction
    out = [_extract_tool(b) for b in blocs]
    # On garde seulement les outils avec au moins un champ non‑vide
    return [o for o in out if any(v is not None for v in o.values())]

# REQUISITION  ────────────────────────
def extract_requisition(text: str) -> Dict[str, Any]:
    return {
        "requisitionStatus"     : _match(text, r"\bstatus\b\s*[:\-]?\s*([\w\-]+)"),
        "description"           : _match(text, r"\bnotes?\b\s*[:\-]?\s*(.+)"),
        "receptionDate"         : _match(text, r"\bdate\b\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})"),
        "customerPurchaseNumber": _match(text, r"\bPO\s*Number\s*[:\-]?\s*([\w\-]+)"),  # W65763‑07
        "contact"               : _match(text, r"\bcontact\b\s*[:\-]?\s*([\w\s]+)"),     # Alex
        "toolNumber"            : _match(text, r"\btool number\b\s*[:\-]?\s*([\w\-]+)"),
        "cavityQuantity"        : _i(_match(text, r"\bhole[s]?\b\s*[:\-]?\s*(\d+)")),    # Holes: 1
        "doubleLayout"          : _b("double layout" in text.lower())
    }

# ─────────── CUSTOMER ───────────
def _extract_customer(block: str) -> Dict[str, Any]:
    return {
        "nickname"       : _match(block, r"\bnick(?:name)?\b\s*[:\-]?\s*([\w\-]+)"),
        "phone"          : _match(block, r"\bphone\b\s*[:\-]?\s*([\d ()\-\.]+)"),
        "billingAddress" : _match(block, r"\bbilling address\b\s*[:\-]?\s*(.+)"),
        "shippingAddress": _match(block, r"\bshipping address\b\s*[:\-]?\s*(.+)"),
        "companyName"    : _match(block, r"\bcompany name\b\s*[:\-]?\s*(.+)")
    }

def extract_customer(text: str) -> List[Dict[str, Any]]:
    # On considère 1 bloc CUSTOMER par page
    bloc = _match(text, r"\bCUSTOMER\b(.+?)(?:\bPROFILE\b|\Z)", 1)
    return [_extract_customer(bloc)] if bloc else []

# ─────────── PROFILE ───────────
def _extract_profile(block: str) -> Dict[str, Any]:
    txt = block.lower()
    return {
        "customerCodePrefix": _match(block, r"\bcustomer code prefix\b\s*[:\-]?\s*([\w\-]+)"),
        "customerCode"      : _match(block, r"\bcustomer code\b\s*[:\-]?\s*([\w\-]+)"),
        "description"       : _match(block, r"\bdescription\b\s*[:\-]?\s*(.+)"),
        "creationDate"      : _match(block, r"\b(creation|date)\b\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})", 2),
        "alloy"             : _match(block, r"\balloy\b\s*[:\-]?\s*([\w\-]+)"),
        "mandrelQuantity"   : _i(_match(block, r"\bmandrel quantity\b\s*[:\-]?\s*(\d+)")),
        "cavityQuantity"    : _i(_match(block, r"\bcavity quantity\b\s*[:\-]?\s*(\d+)")),
        "interlock"         : _b("interlock" in txt),
        "zsc"               : _f(_match(block, r"\bzsc\b\s*[:\-]?\s*([\d.,]+)")),
        "doubleLayoutAngle" : _f(_match(block, r"\bdouble layout angle\b\s*[:\-]?\s*([\d.,]+)")),
        "hasElectrode"      : _b("electrode" in txt),
        "hasMicrofinish"    : _b("microfinish" in txt)
    }

def extract_profile(text: str) -> List[Dict[str, Any]]:
    return [_extract_profile(b) for b in _split_on("PROFILE", text)]



# ─────────── Router principal ───────────
def extract_data_with_regex(text: str) -> List[Dict[str, Any]]:
    results : List[Dict[str,Any]] = []
    for d in extract_piece(text):    results.append({"model":"piece",    **d})
    for d in extract_tool(text):     results.append({"model":"tool",     **d})
    for d in extract_profile(text):  results.append({"model":"profile",  **d})
    for d in extract_customer(text): results.append({"model":"customer", **d})

    req = extract_requisition(text)
    if any(req.values()):            results.append({"model":"requisition", **req})
    return results
