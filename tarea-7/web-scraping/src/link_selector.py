# src/link_selector.py
import os
import json
import subprocess
import logging
from typing import List, Dict
from .utils import safe_json_loads

# Configuración del registro de logs
logger = logging.getLogger(__name__)

# Variables de entorno para configurar el uso de Ollama
OLLAMA_METHOD = os.getenv("OLLAMA_METHOD", "cli")            # Método: CLI o HTTP
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")           # Modelo a usar
OLLAMA_HTTP_URL = os.getenv("OLLAMA_HTTP_URL", "http://localhost:11434")  # URL del servidor Ollama
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("1", "true", "yes")  # Modo simulación (mock)

# Carga de los prompts del sistema y del usuario
LINK_SYSTEM_PROMPT = open("prompts/link_system.md", "r", encoding="utf-8").read()
LINK_USER_PROMPT = open("prompts/link_user.md", "r", encoding="utf-8").read()

def call_ollama_cli(prompt: str) -> str:
    """
    Llama al modelo Ollama usando la línea de comandos (CLI).
    """
    # Comando base de ejemplo; la sintaxis puede variar según la versión de Ollama
    cmd = ["ollama", "generate", OLLAMA_MODEL, "--prompt", prompt]
    
    # Ejecuta el comando en la terminal
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        capture_output=True, text=True
    )

    # Si hay error, se registra y lanza excepción
    if result.returncode != 0:
        logger.error("Ollama CLI error: %s", result.stderr)
        raise RuntimeError(result.stderr)
    
    # Devuelve la salida del modelo
    return result.stdout

def call_ollama_http(prompt: str) -> str:
    """
    Llama al modelo Ollama usando una petición HTTP (API REST).
    """
    import requests
    # Construye la URL final del endpoint
    url = OLLAMA_HTTP_URL.rstrip("/") + "/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt}

    # Envía la solicitud al servidor de Ollama
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

    # Devuelve el texto de la respuesta
    return r.text

def call_ollama(prompt: str) -> str:
    """
    Llama al modelo Ollama usando el método configurado (mock, HTTP o CLI).
    """
    if MOCK_MODE:
        # Respuesta simulada para pruebas sin conexión al modelo
        mock = {
            "links": [
                {"type": "about page", "url": "https://example.com/about"},
                {"type": "careers page", "url": "https://example.com/careers"}
            ]
        }
        return json.dumps(mock)
    
    # Selecciona el método de conexión según configuración
    if OLLAMA_METHOD == "http":
        return call_ollama_http(prompt)
    else:
        return call_ollama_cli(prompt)

def select_relevant_links(base_url: str, urls: List[str]) -> Dict:
    """
    Envía una lista de URLs al modelo para que seleccione los enlaces más relevantes.
    """
    # Construye el prompt combinando el texto del sistema y del usuario
    payload = LINK_SYSTEM_PROMPT + "\n\n" + LINK_USER_PROMPT.format(
        base_url=base_url,
        links=json.dumps(urls, ensure_ascii=False, indent=2)
    )

    # Llama al modelo con el prompt generado
    raw = call_ollama(payload)

    try:
        # Intenta interpretar la respuesta como JSON
        parsed = safe_json_loads(raw)
        return parsed
    except Exception as e:
        # Si falla la carga, registra el error y lanza excepción
        logger.error("LLM no devolvió JSON limpio, intentando reparar: %s", e)
        raise
