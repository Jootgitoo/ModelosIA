# src/scraping.py
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from urllib import robotparser
from pathlib import Path
from typing import List, Tuple
from .utils import get_user_agent, rate_limit_sleep

# Configuración del logger para registrar eventos
logger = logging.getLogger(__name__)

# Tiempo máximo de espera en las peticiones HTTP
DEFAULT_TIMEOUT = 10

def can_fetch(url: str) -> bool:
    """
    Comprueba si está permitido hacer scraping en la URL según el archivo robots.txt.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        # Si no se puede acceder al robots.txt, se asume que el acceso está permitido
        logger.info("No robots.txt accesible (%s): %s", robots_url, e)
        return True
    # Devuelve True si el scraping está permitido para nuestro user-agent
    return rp.can_fetch(get_user_agent(), url)

def fetch(url: str, session: requests.Session = None) -> Tuple[int, str]:
    """
    Descarga el contenido HTML de una página web.
    """
    session = session or requests.Session()
    headers = {"User-Agent": get_user_agent()}
    try:
        # Envía la petición HTTP con un timeout
        resp = session.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()  # Lanza error si el código no es 2xx
        logger.info("Fetched %s (%d)", url, resp.status_code)
        return resp.status_code, resp.text
    except requests.RequestException as e:
        # Registra errores de conexión o respuesta
        logger.error("Error fetching %s: %s", url, e)
        raise

def extract_links(html: str, base_url: str) -> List[str]:
    """
    Extrae todos los enlaces (etiquetas <a>) del HTML y los convierte en URLs absolutas.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Elimina etiquetas innecesarias que pueden interferir
    for tag in soup(["script", "style", "noscript", "svg", "img", "input", "button", "meta"]):
        tag.decompose()

    links = set()
    # Recorre todas las etiquetas <a> con atributo href
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        if href:
            # Convierte URLs relativas en absolutas
            abs_url = urljoin(base_url, href)
            links.add(abs_url)

    # Devuelve una lista única de enlaces
    return list(links)

def scrape_and_extract(url: str, session: requests.Session = None, rate_limit: float = 0.6):
    """
    Descarga una página, respeta las reglas de robots.txt, y extrae sus enlaces.
    """
    # Verifica si el scraping está permitido
    if not can_fetch(url):
        raise PermissionError(f"Scraping bloqueado por robots.txt: {url}")

    # Usa la sesión existente o crea una nueva
    session = session or requests.Session()

    # Descarga la página
    status, html = fetch(url, session=session)

    # Espera un tiempo entre peticiones (para no saturar el servidor)
    time.sleep(rate_limit_sleep(rate_limit))

    # Extrae los enlaces de la página descargada
    links = extract_links(html, base_url=url)

    # Devuelve el HTML y los enlaces encontrados
    return html, links
