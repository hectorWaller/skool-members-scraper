import json
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

class ExportManager:
    """Handles exporting records to JSON, CSV, or XLSX."""

    @staticmethod
    def _ensure_parent(path: str):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def to_json(self, records: List[Dict[str, Any]], path: str):
        p = self._ensure_parent(path)
        with p.open("w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def to_csv(self, records: List[Dict[str, Any]], path: str):
        p = self._ensure_parent(path)
        df = pd.json_normalize(records)
        df.to_csv(p, index=False)

    def to_xlsx(self, records: List[Dict[str, Any]], path: str):
        p = self._ensure_parent(path)
        df = pd.json_normalize(records)
        df.to_excel(p, index=False)