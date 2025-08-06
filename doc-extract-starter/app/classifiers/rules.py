import yaml, re
from typing import Dict, Any, List

class RulesClassifier:
    def __init__(self, variants: List[Dict[str, Any]]):
        self.variants = variants

    def classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        best = None
        for v in self.variants:
            anchors = [a.lower() for a in v.get("identify", {}).get("anchors_all_of", [])]
            if anchors and all(a in text_lower for a in anchors):
                score = len(anchors)
                item = {"variant_id": v["variant_id"], "score": score, "reason": f"anchors_all_of={anchors}"}
                if not best or item["score"] > best["score"]:
                    best = item
        if best:
            return {"variant_id": best["variant_id"], "confidence": min(0.99, 0.6 + 0.1*best["score"]), "evidence": best["reason"]}
        return {"variant_id": None, "confidence": 0.0, "evidence": "no anchors matched"}
