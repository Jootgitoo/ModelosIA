# src/link_selector.py
import os
import json
import subprocess
import logging
from typing import List, Dict
from .utils import safe_json_loads

logger = logging.getLogger(__name__)

OLLAMA_METHOD = os.getenv("OLLAMA_METHOD", "cli")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_HTTP_URL = os.getenv("OLLAMA_HTTP_URL", "http://localhost:11434")
MOCK_MODE = os.getenv("MOCK_MODE","false").lower() in ("1","true","yes")

LINK_SYSTEM_PROMPT = open("prompts/link_system.md","r",encoding="utf-8").read()
LINK_USER_PROMPT = open("prompts/link_user.md","r",encoding="utf-8").read()

def call_ollama_cli(prompt: str) -> str:
    # nota: la sintaxis exacta de ollama CLI puede variar; intentamos usar 'ollama generate'
    cmd = ["ollama", "generate", OLLAMA_MODEL, "--prompt", prompt]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        logger.error("Ollama CLI error: %s", result.stderr)
        raise RuntimeError(result.stderr)
    return result.stdout

def call_ollama_http(prompt: str) -> str:
    import requests
    url = OLLAMA_HTTP_URL.rstrip("/") + "/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.text

def call_ollama(prompt: str) -> str:
    if MOCK_MODE:
        # respuesta mock simple para testing
        mock = {"links":[{"type":"about page","url":"https://example.com/about"},{"type":"careers page","url":"https://example.com/careers"}]}
        return json.dumps(mock)
    if OLLAMA_METHOD == "http":
        return call_ollama_http(prompt)
    else:
        return call_ollama_cli(prompt)

def select_relevant_links(base_url: str, urls: List[str]) -> Dict:
    # construir prompt: incluye system + user
    payload = LINK_SYSTEM_PROMPT + "\n\n" + LINK_USER_PROMPT.format(base_url=base_url, links=json.dumps(urls, ensure_ascii=False, indent=2))
    raw = call_ollama(payload)
    try:
        parsed = safe_json_loads(raw)
        return parsed
    except Exception as e:
        logger.error("LLM no devolvió JSON limpio, intentando reparar: %s", e)
        # intentar recuperar usando safe_json_loads ya hace el repair o raise
        raise
