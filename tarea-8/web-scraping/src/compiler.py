import time
import logging
import requests
from bs4 import BeautifulSoup
from .scraping import fetch
from .utils import slug, rate_limit_sleep

logger = logging.getLogger(__name__)

def clean_text_from_html(html: str) -> str:
    """
    Limpia el HTML y devuelve solo el texto legible.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "form", "img", "svg", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # límite de seguridad para evitar respuestas enormes
    return "\n\n".join(lines[:1500])


def compile_pages(selected_links, session=None, rate_limit=0.6):
    """
    Descarga, limpia y unifica el contenido de las páginas seleccionadas.

    Devuelve un único string unificado.
    """
    # Si no se proporciona una sesión HTTP, se crea una nueva
    session = session or requests.Session()

    # Lista donde se irá acumulando el texto limpio de todas las páginas
    unified_text = []

    # Se extrae la lista de enlaces desde el diccionario recibido
    links = selected_links.get("links", [])

    logger.info("Compilando %d páginas seleccionadas por el LLM...", len(links))

    # Recorre cada enlace seleccionado
    for item in links:
        url = item["url"]
        typ = item.get("type", "other")  # Tipo de página (opcional)
        score = item.get("score")        # Puntuación asignada (opcional)

        logger.info("Descargando %s (tipo=%s, score=%s)", url, typ, score)

        try:
            # Se descarga el HTML de la página usando la función fetch()
            _, html = fetch(url, session=session)

            # Se limpia el HTML para obtener solo el texto útil
            cleaned = clean_text_from_html(html)

            # Se construye una sección formateada y se almacena
            unified_text.append(
                f"# Página: {url}\n"
                f"## Tipo: {typ}\n"
                f"{cleaned}\n\n"
                "----------------------------------------\n\n"
            )

            # Pausa entre peticiones según el rate limit
            time.sleep(rate_limit_sleep(rate_limit))

        except Exception as e:
            # Si ocurre un error con alguna página, se registra pero el proceso continúa
            logger.error("Error al compilar %s: %s", url, e)

    # Devuelve un único string con todas las páginas unificadas
    return "\n".join(unified_text)
