import yaml, os
from typing import List, Dict, Any

def load_variants(config_dir: str) -> List[Dict[str, Any]]:
    out = []
    vdir = os.path.join(config_dir, "variants")
    for name in os.listdir(vdir):
        if not name.endswith(".yaml"):
            continue
        with open(os.path.join(vdir, name), "r") as f:
            out.append(yaml.safe_load(f))
    return out

def load_field_dict(config_dir: str) -> Dict[str, Any]:
    with open(os.path.join(config_dir, "field_dictionary.yaml"), "r") as f:
        return yaml.safe_load(f)
