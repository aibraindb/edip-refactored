# Document Extract Starter — Lease/Loan Agreements (DocuSign)

A minimal, **extensible** service that classifies and extracts fields from **Lease/Loan agreements**, with a focus on agreements signed via **DocuSign** (e.g., presence of "DocuSign Envelope ID").

> **This starter is text-native only** (uses `pdfminer.six`). For scanned PDFs, add OCR (PaddleOCR/Tesseract) as a next step.

## Features
- Variant registry via YAML (start with `lease_docusign_v1`).
- Anchors-based **classifier** (rules) for fast, explainable routing.
- Regex + anchor-window **extractors** on plain text.
- Cross-field **validators** (totals math placeholder).
- FastAPI endpoints: `/classify`, `/extract`.
- CLI for batch extraction.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run the API
uvicorn app.api.main:app --reload --port 8000
# Then open http://localhost:8000/docs
```

### CLI (batch extraction)
```bash
python scripts/extract_folder.py --input ./data/samples --output ./data/out.jsonl
```

## Add your own variants
1. Duplicate `config/variants/lease_docusign_v1.yaml` and change `variant_id`/anchors.
2. Add/modify field regex and anchors under `extract.fields`.
3. Restart the service — no code changes required.

## Notes
- For scanned PDFs, integrate OCR and a layout-aware extractor.
- To add a validation UI, wrap results in a small Streamlit/React tool.
- Keep corrections and feedback for continuous learning.
