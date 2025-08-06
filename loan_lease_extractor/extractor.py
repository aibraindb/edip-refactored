
import re
import io
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

# Lightweight PDF text extraction via pdfminer.six (used internally by pdfplumber).
# We avoid heavy CV deps; provide OCR fallback hook if user installs extras.

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

@dataclass
class ExtractedField:
    key: str
    value: str
    page: int
    method: str
    confidence: float = 0.7

@dataclass
class ExtractionResult:
    text_by_page: List[str]
    fields: List[ExtractedField] = field(default_factory=list)
    dynamic_schema: Dict[str, Any] = field(default_factory=dict)

DEFAULT_HINTS = {
    "borrower_name": [r"Borrower\s*Name[:\-]\s*(?P<val>.+)"],
    "lender_name": [r"Lender\s*Name[:\-]\s*(?P<val>.+)"],
    "loan_number": [r"(Loan|Account)\s*(No\.?|Number)[:\-]\s*(?P<val>[A-Z0-9\-]+)"],
    "loan_amount": [r"(Loan|Principal)\s*Amount[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)"],
    "interest_rate": [r"(Interest\s*Rate|APR)[:\-]\s*(?P<val>\d+(?:\.\d+)?\s*%?)"],
    "effective_date": [r"(Effective|Start)\s*Date[:\-]\s*(?P<val>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"],
    "maturity_date": [r"(Maturity|End)\s*Date[:\-]\s*(?P<val>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"],
    "payment_frequency": [r"Payment\s*Frequency[:\-]\s*(?P<val>(Monthly|Quarterly|Bi-Weekly|Weekly|Annual))"],
    "monthly_payment": [r"(Monthly\s*Payment|EMI)[:\-]\s*\$?(?P<val>[\d,]+(?:\.\d{2})?)"],
    "guarantor_name": [r"(Guarantor|Surety)\s*Name[:\-]\s*(?P<val>.+)"],
    "address": [r"(Property|Premises)\s*Address[:\-]\s*(?P<val>.+)"],
}

KEY_VALUE_LINE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 \/\-\(\)&]+?)\s*[:\-]\s*(.+?)\s*$")

def load_hints(path: str) -> Dict[str, List[str]]:
    import json, os
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_HINTS

def read_pdf_text(pdf_path: str) -> List[str]:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber not installed. Please `pip install pdfplumber`")
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            pages_text.append(p.extract_text() or "")
    return pages_text

def regex_extract(text_by_page: List[str], hints: Dict[str, List[str]]) -> List[ExtractedField]:
    fields = []
    for page_idx, txt in enumerate(text_by_page, start=1):
        for key, patterns in hints.items():
            for pat in patterns:
                try:
                    for m in re.finditer(pat, txt, flags=re.IGNORECASE):
                        val = m.groupdict().get("val") or m.group(0)
                        fields.append(ExtractedField(key=key, value=val.strip(), page=page_idx, method=f"regex:{pat}", confidence=0.85))
                except re.error:
                    # bad pattern, skip
                    continue
        # generic key:value lines
        for line in txt.splitlines():
            m = KEY_VALUE_LINE.match(line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                # normalize key to snake_case-ish
                norm_k = re.sub(r"[^a-z0-9]+", "_", k.lower()).strip("_")
                fields.append(ExtractedField(key=norm_k, value=v, page=page_idx, method="kv-line", confidence=0.6))
    return fields

def consolidate(fields: List[ExtractedField]) -> Dict[str, Any]:
    schema = {}
    for f in fields:
        if f.key in schema:
            existing = schema[f.key]
            # promote to list if different values
            if isinstance(existing, list):
                if f.value not in [x["value"] if isinstance(x, dict) else x for x in existing]:
                    existing.append({"value": f.value, "page": f.page, "confidence": f.confidence})
            else:
                if f.value != existing:
                    schema[f.key] = [existing, {"value": f.value, "page": f.page, "confidence": f.confidence}]
        else:
            # keep provenance
            schema[f.key] = {"value": f.value, "page": f.page, "confidence": f.confidence}
    return schema

def extract(pdf_path: str, hints_path: str = "") -> ExtractionResult:
    hints = load_hints(hints_path)
    pages = read_pdf_text(pdf_path)
    fields = regex_extract(pages, hints)
    schema = consolidate(fields)
    return ExtractionResult(text_by_page=pages, fields=fields, dynamic_schema=schema)
