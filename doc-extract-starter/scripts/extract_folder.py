import argparse, os, json
from app.config_loader import load_variants
from app.classifiers.rules import RulesClassifier
from app.extractors.primitives import run_regex, run_literal, run_anchor_window
from app.pdf_text import extract_pdf_text
import yaml

def extract_one(path, variants):
    text = extract_pdf_text(path)
    if not text:
        return {"path": path, "error": "no_text"}
    clf = RulesClassifier(variants)
    c = clf.classify(text)
    vid = c.get("variant_id")
    profile = next((v for v in variants if v.get("variant_id")==vid), None)
    if not profile:
        return {"path": path, "classification": c, "error": "no_variant"}
    # extract
    out_fields = {}
    for fname, cfg in profile.get("extract", {}).get("fields", {}).items():
        strat = cfg.get("strategy")
        if strat == "regex":
            val, conf, ev = run_regex(text, cfg)
        elif strat == "literal":
            val, conf, ev = run_literal(text, cfg)
        elif strat == "anchor_window":
            val, conf, ev = run_anchor_window(text, cfg)
        else:
            val, conf, ev = None, 0.0, {"reason": f"unknown strategy {strat}"}
        out_fields[fname] = {"value": val, "confidence": conf, "evidence": ev}
    return {"path": path, "classification": c, "fields": out_fields}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder with PDFs")
    ap.add_argument("--output", required=True, help="Output JSONL file")
    ap.add_argument("--config", default="config", help="Config dir")
    args = ap.parse_args()

    variants = load_variants(args.config)
    with open(args.output, "w") as fout:
        for name in os.listdir(args.input):
            if not name.lower().endswith(".pdf"):
                continue
            path = os.path.join(args.input, name)
            res = extract_one(path, variants)
            fout.write(json.dumps(res) + "\n")
            print(f"Processed {name}")

if __name__ == "__main__":
    main()
