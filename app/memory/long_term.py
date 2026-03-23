from pathlib import Path
import json
from typing import Dict


BASE_DIR = Path("outputs/memory/semantic")
BASE_DIR.mkdir(parents=True, exist_ok=True)
PREFER_PATH = BASE_DIR / "preferences.json"


def load_preferences() -> Dict:
    if not PREFER_PATH.exists():
        return {}
    return json.loads(PREFER_PATH.read_text(encoding="utf-8"))


def save_preferences(prefs: Dict):
    PREFER_PATH.write_text(
        json.dumps(prefs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_preferences_from_query(query: str):
    prefs = load_preferences()
    q = query.lower()

    if "默认渠道" in query and "ads" in q:
        prefs["default_channel"] = "ads"
    elif "默认渠道" in query and "seo" in q:
        prefs["default_channel"] = "seo"

    if "以后都输出详细版" in query:
        prefs["report_style"] = "detailed"
    elif "以后都输出简洁版" in query:
        prefs["report_style"] = "brief"

    save_preferences(prefs)
