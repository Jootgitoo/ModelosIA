# src/utils.py
import os
import time
import json
import logging
import slugify
from pathlib import Path

logger = logging.getLogger(__name__)

def get_user_agent():
    return os.getenv("USER_AGENT", "BrochureAI/1.0 (+https://example)")

def rate_limit_sleep(rate_limit_seconds: float):
    # devuelve valor a dormir; aquí dejamos como identidad para centralizar
    return rate_limit_seconds

def save_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_text(path):
    return Path(path).read_text(encoding="utf-8")

def safe_json_loads(s: str):
    try:
        return json.loads(s)
    except Exception:
        # intento de "repair" sencillo
        import re
        found = re.search(r'(\{.*\})', s, flags=re.S)
        if found:
            try:
                return json.loads(found.group(1))
            except Exception:
                pass
        raise

def slug(name: str) -> str:
    return slugify(name)[:50]
