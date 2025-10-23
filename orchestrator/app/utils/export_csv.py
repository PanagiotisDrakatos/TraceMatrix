import os, csv
from typing import Iterable, Dict

# Safe default: exports directory under app root
try:
    from ..config import EXPORT_DIR as _EXPORT_DIR
except Exception:
    _EXPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "exports"))

HEADER = ["type","value","title","url","source"]

def ensure_dir():
    os.makedirs(_EXPORT_DIR, exist_ok=True)

def export_entities(rows: Iterable[Dict]) -> str:
    ensure_dir()
    path = os.path.join(_EXPORT_DIR, "entities.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in HEADER})
    return path
