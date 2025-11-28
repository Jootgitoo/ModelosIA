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

import json
import re

def safe_json_loads(s: str):
    """
    Intenta parsear JSON de forma segura, limpiando markdown y texto adicional.
    
    Args:
        s: String que contiene JSON (posiblemente con texto adicional)
    
    Returns:
        Objeto Python parseado desde JSON
    
    Raises:
        json.JSONDecodeError: Si el JSON es inválido después de limpiar
    """
    if not s or not s.strip():
        raise json.JSONDecodeError("Empty string", s, 0)
    
    s = s.strip()
    
    # 1. Intentar parsear directamente
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    
    # 2. Extraer de bloques markdown (```json ... ``` o ``` ... ```)
    markdown_patterns = [
        r'```json\s*\n(.*?)\n```',
        r'```\s*\n(.*?)\n```',
        r'```json\s*(.*?)```',
        r'```(.*?)```'
    ]
    
    for pattern in markdown_patterns:
        match = re.search(pattern, s, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                continue
    
    # 3. Buscar objeto JSON completo con llaves balanceadas
    # Encuentra todas las posiciones de '{'
    for i in range(len(s)):
        if s[i] == '{':
            # Intentar encontrar el cierre balanceado
            brace_count = 0
            for j in range(i, len(s)):
                if s[j] == '{':
                    brace_count += 1
                elif s[j] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Encontramos un objeto JSON completo
                        json_candidate = s[i:j+1]
                        try:
                            return json.loads(json_candidate)
                        except json.JSONDecodeError:
                            # Este no era válido, seguir buscando
                            break
            # Si no encontramos cierre, continuar con el siguiente '{'
    
    # 4. Buscar array JSON completo con corchetes balanceados
    for i in range(len(s)):
        if s[i] == '[':
            bracket_count = 0
            for j in range(i, len(s)):
                if s[j] == '[':
                    bracket_count += 1
                elif s[j] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_candidate = s[i:j+1]
                        try:
                            return json.loads(json_candidate)
                        except json.JSONDecodeError:
                            break
    
    # Si todo falla, mostrar información de depuración
    preview = s[:200] + "..." if len(s) > 200 else s
    raise json.JSONDecodeError(
        f"No valid JSON found. Preview: {preview}", 
        s, 
        0
    )
    


def slug(name: str) -> str:
    """
    Genera una versión 'slug' (nombre seguro para archivos/URLs) del texto recibido.
    Limita la longitud a 50 caracteres.
    """
    return slugify(name)[:50]

def sanitize_markdown(md: str) -> str:
    lines = [ln.rstrip() for ln in md.splitlines()]
    return "\n".join(lines).strip()

