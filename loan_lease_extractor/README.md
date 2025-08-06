
# Loan/Lease Dynamic Schema Extractor (Streamlit)

A minimal Streamlit app to extract key–value information from loan/lease PDFs and build a dynamic schema. 
Includes a synthetic sample PDF to test quickly. Extendable to invoices by adding invoice-specific hints.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then upload your own PDF or use `sample_docs/sample_loan.pdf` for a dry run.
Optionally upload `schema_presets/loan_lease_hints.json` to improve extraction.

## How it works
- **pdfplumber** extracts text per page.
- **Regex hints** catch common loan/lease fields (loan amount, interest rate, etc.).
- Generic `key: value` lines are also parsed to grow a **dynamic schema**.
- Provenance (page, method, confidence) is kept per field.

## Extending to invoices
1. Create `schema_presets/invoice_hints.json` with invoice-specific fields (invoice_number, vendor, total, tax, PO, etc.).
2. Add post-processing (e.g., currency normalization, date parsing).

## Optional OCR
For scanned PDFs, install OCR deps and add a fallback in `extractor.py`:
- `pdf2image`, `pytesseract`, `Pillow`

## Notes
This is a lightweight baseline. For production IDP you may add:
- Layout-based parsing (e.g., table detection)
- Classifiers per document type
- Confidence calibration, validation rules
- Export to JSON/CSV and connectors to ECM/RPA systems
