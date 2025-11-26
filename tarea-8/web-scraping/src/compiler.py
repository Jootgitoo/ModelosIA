import time
import logging
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

    selected_links -> dict con:
    { "links": [ { "url": "...", "type": "...", "score": ..., "rationale": "..." }, ... ] }

    Devuelve un único string unificado.
    """
    session = session or requests.Session()

    unified_text = []
    links = selected_links.get("links", [])

    logger.info("Compilando %d páginas seleccionadas por el LLM...", len(links))

    for item in links:
        url = item["url"]
        typ = item.get("type", "other")
        score = item.get("score")

        logger.info("Descargando %s (tipo=%s, score=%s)", url, typ, score)

        try:
            _, html = fetch(url, session=session)
            cleaned = clean_text_from_html(html)

            unified_text.append(
                f"# Página: {url}\n"
                f"## Tipo: {typ}\n"
                f"{cleaned}\n\n"
                "----------------------------------------\n\n"
            )

            # Respetar rate limit
            time.sleep(rate_limit_sleep(rate_limit))

        except Exception as e:
            logger.error("Error al compilar %s: %s", url, e)

    # Resultado final para LLM2: texto unificado
    return "\n".join(unified_text)
