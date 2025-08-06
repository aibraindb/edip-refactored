import re
from typing import Dict, Any, Tuple, List, Optional

MoneyPattern = r"[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})"

def _compile_patterns(patterns: List[str]):
    return [re.compile(p, re.IGNORECASE) for p in patterns]

def run_regex(text: str, cfg: Dict[str, Any]) -> Tuple[Optional[str], float, Dict[str, Any]]:
    pats = _compile_patterns(cfg.get("patterns", []))
    for pat in pats:
        m = pat.search(text)
        if not m:
            continue
        # choose the last captured group if multiple
        groups = [g for g in m.groups() if g is not None]
        if groups:
            val = groups[-1].strip()
        else:
            val = m.group(0).strip()
        return val, 0.85, {"pattern": pat.pattern}
    return None, 0.0, {"reason": "no regex match"}

def run_literal(_: str, cfg: Dict[str, Any]):
    return cfg.get("value"), 0.99, {"reason": "literal"}

def run_anchor_window(text: str, cfg: Dict[str, Any]):
    anchor = cfg.get("anchor")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if anchor.lower() in line.lower():
            offset = cfg.get("window_lines_after", 1)
            j = min(i + offset, len(lines)-1)
            candidate = lines[j].strip()
            # strip label-like prefixes
            candidate = re.sub(r"^(:|\s*[-–•:]\s*)", "", candidate).strip()
            return candidate, 0.7, {"anchor": anchor, "line": i, "picked": j}
    return None, 0.0, {"reason": "anchor not found", "anchor": anchor}
