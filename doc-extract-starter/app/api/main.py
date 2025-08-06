from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import tempfile, os

from app.config_loader import load_variants, load_field_dict
from app.classifiers.rules import RulesClassifier
from app.extractors.primitives import run_regex, run_literal, run_anchor_window
from app.pdf_text import extract_pdf_text
from app.validators.totals import validate_totals

CONFIG_DIR = os.environ.get("CONFIG_DIR", "config")

app = FastAPI(title="Doc Extract — Lease/Loan (DocuSign)")

_variants = load_variants(CONFIG_DIR)
_fields = load_field_dict(CONFIG_DIR)
_classifier = RulesClassifier(_variants)

def _extract_with_profile(text: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    fields = profile.get("extract", {}).get("fields", {})
    result = {}
    for fname, cfg in fields.items():
        strat = cfg.get("strategy")
        if strat == "regex":
            val, conf, ev = run_regex(text, cfg)
        elif strat == "literal":
            val, conf, ev = run_literal(text, cfg)
        elif strat == "anchor_window":
            val, conf, ev = run_anchor_window(text, cfg)
        else:
            val, conf, ev = None, 0.0, {"reason": f"unknown strategy {strat}"}
        result[fname] = {"value": val, "confidence": conf, "evidence": ev}
    result["_validation"] = validate_totals({k:v.get("value") for k,v in result.items()})
    return result

@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    text = extract_pdf_text(tmp_path)
    os.unlink(tmp_path)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to read PDF text (is it scanned?)")
    res = _classifier.classify(text)
    return JSONResponse(res)

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    text = extract_pdf_text(tmp_path)
    os.unlink(tmp_path)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to read PDF text (is it scanned?)")
    # classify
    res = _classifier.classify(text)
    vid = res.get("variant_id")
    profile = None
    for v in _variants:
        if v.get("variant_id") == vid:
            profile = v
            break
    if not profile:
        # fallback: try default profile if any
        raise HTTPException(status_code=422, detail=f"No variant matched; evidence={res.get('evidence')}")
    fields = _extract_with_profile(text, profile)
    out = {"variant": vid, "classification": res, "fields": fields}
    return JSONResponse(out)
