# services/regex_parser.py

import re

def extract_data_with_regex(text):
    """
    Applique des regex pour extraire des données structurées du texte OCRisé.
    """
    data = {}

    # PO Number
    match_po = re.search(r"PO\s*Number\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    if match_po:
        data["po_number"] = match_po.group(1)

    # Order Date
    match_order_date = re.search(r"Order\s*Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    if match_order_date:
        data["order_date"] = match_order_date.group(1)

    # Vendor
    match_vendor = re.search(r"Vendor\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    if match_vendor:
        data["vendor_id"] = match_vendor.group(1)

    # Part Number
    match_part = re.search(r"(MW[-−]\d+)", text)
    if match_part:
        data["part_number"] = match_part.group(1)

    # Dimensions (ex: 11 x 6.406)
    match_dim = re.search(r"(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)", text)
    if match_dim:
        data["width"] = float(match_dim.group(1))
        data["height"] = float(match_dim.group(2))

    # Unit Price
    match_unit_price = re.search(r"Unit\s+Price\s*[:\-]?\s*([\d,]+\.\d+)", text)
    if match_unit_price:
        data["unit_price"] = float(match_unit_price.group(1).replace(",", ""))

    # Total
    match_total = re.search(r"Total\s*[:\-]?\s*([\d,]+\.\d+)", text)
    if match_total:
        data["total_price"] = float(match_total.group(1).replace(",", ""))

    # Date générique de secours (fallback)
    match_date = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    if match_date and "order_date" not in data:
        data["date"] = match_date.group(1)

    return data
