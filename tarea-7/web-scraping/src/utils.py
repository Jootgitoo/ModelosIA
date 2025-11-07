# src/utils.py
import os
import time
import json
import logging
from slugify import slugify
from pathlib import Path

# Configuración del registro de logs
logger = logging.getLogger(__name__)

def get_user_agent():
    """
    Devuelve el User-Agent que se usará en las peticiones HTTP.
    """
    return os.getenv("USER_AGENT", "BrochureAI/1.0 (+https://example)")

def rate_limit_sleep(rate_limit_seconds: float):
    """
    Devuelve el tiempo (en segundos) que debe esperarse entre peticiones.
    Actualmente actúa como función identidad.
    """
    return rate_limit_seconds

def save_text(path, text):
    """
    Guarda texto en un archivo, creando directorios si es necesario.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)  # Crea carpetas si no existen
    path.write_text(text, encoding="utf-8")         # Escribe el texto en el archivo

def load_text(path):
    """
    Carga el contenido de texto de un archivo.
    """
    return Path(path).read_text(encoding="utf-8")

def safe_json_loads(s: str):
    """
    Intenta cargar un string JSON de forma segura.
    Si el formato no es válido, busca un bloque JSON dentro del texto y lo intenta parsear.
    """
    try:
        # Intenta convertir directamente a JSON
        return json.loads(s)
    except Exception:
        # Si falla, busca una posible estructura JSON dentro del texto
        import re
        found = re.search(r'(\{.*\})', s, flags=re.S)
        if found:
            try:
                return json.loads(found.group(1))
            except Exception:
                pass
        # Si no se logra parsear, lanza la excepción
        raise

def slug(name: str) -> str:
    """
    Genera una versión 'slug' (nombre seguro para archivos/URLs) del texto recibido.
    Limita la longitud a 50 caracteres.
    """
    return slugify(name)[:50]
