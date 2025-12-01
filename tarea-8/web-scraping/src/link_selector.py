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
    Ejecuta Ollama por CLI en Windows
    """
    try:
        import subprocess

        process = subprocess.Popen(
            ["ollama", "run", OLLAMA_MODEL],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # IMPORTANTE: enviamos el prompt en bytes UTF-8
        stdout, stderr = process.communicate(
            input=prompt.encode("utf-8"),
            timeout=120
        )

        if process.returncode != 0:
            raise RuntimeError(stderr.decode("utf-8", errors="ignore"))

        return stdout.decode("utf-8", errors="ignore")

    except Exception as e:
        logger.error("Error ejecutando Ollama CLI: %s", e)
        raise



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
    
    
def select_relevant_links(base_url: str, items: List[Dict]) -> Dict:
    """
    Envía una lista de enlaces con snippet al LLM para seleccionar los más relevantes.
    items debe ser una lista de dicts: { "url": "...", "snippet": "..." }
    """

    # Convertimos los items a JSON para insertarlos en el prompt
    links_json = json.dumps(items, ensure_ascii=False, indent=2)

    # Construcción del prompt final (system + user)
    payload = (
        LINK_SYSTEM_PROMPT.replace("{base_url}", base_url)
        + "\n\n"
        + LINK_USER_PROMPT.format(
            base_url=base_url,
            links=links_json
        )
    )

    logger.info("Enviando %d enlaces al LLM para análisis...", len(items))

    # Llamada al modelo
    raw_response = call_ollama(payload)

    # Intento de parseo JSON limpio
    try:
        parsed = safe_json_loads(raw_response)
    except Exception as e:
        logger.error("El modelo NO devolvió JSON válido. Respuesta bruta: %s", raw_response)
        raise RuntimeError(f"JSON inválido devuelto por LLM: {e}")

    # Validación del schema mínimo exigido por la práctica
    try:
        validate_schema(parsed)
    except Exception as e:
        logger.error("JSON no cumple el schema requerido: %s", parsed)
        raise

    # Filtrado: score >= 60 (requisito de la Tarea 8)
    filtered = [
        item for item in parsed["links"]
        if int(item.get("score", 0)) >= 60
    ]

    logger.info("De %d enlaces sugeridos por el LLM, %d superan el score mínimo.",
                len(parsed["links"]), len(filtered))

    # Devolvemos solo los enlaces aprobados
    return {"links": filtered}



def validate_schema(parsed: dict):
    # 1. Verifica que exista la clave principal "links"
    if "links" not in parsed:
        raise ValueError("El JSON no tiene clave 'links'.")

    # 2. Comprueba que "links" sea una lista (como se espera)
    if not isinstance(parsed["links"], list):
        raise ValueError("'links' debe ser una lista.")

    # 3. Recorre cada objeto dentro de la lista "links"
    for obj in parsed["links"]:
        # 4. Cada objeto debe contener los campos obligatorios:
        #    "type", "url", "score" y "rationale"
        for key in ("type", "url", "score", "rationale"):
            if key not in obj:
                # Si falta alguno, lanza un error indicando cuál falta
                raise ValueError(f"Falta el campo obligatorio '{key}' en {obj}.")

