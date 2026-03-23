from pathlib import Path
import json
from typing import List, Dict


BASE_DIR = Path("outputs/memory/working")


def _path(session_id: str) -> Path:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    return BASE_DIR / f"{session_id}.json"


def load_working_memory(session_id: str) -> List[Dict]:
    path = _path(session_id)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def append_working_memory(session_id: str, record: Dict):
    items = load_working_memory(session_id)
    items.append(record)
    items = items[-10:]
    _path(session_id).write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
