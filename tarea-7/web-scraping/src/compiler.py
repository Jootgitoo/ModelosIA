# src/compiler.py
from bs4 import BeautifulSoup
from .scraping import fetch
from .utils import slug
import logging

# Configuración del registro de logs
logger = logging.getLogger(__name__)

def clean_text_from_html(html: str) -> str:
    """
    Limpia el contenido HTML y extrae solo el texto legible.
    """
    # Analiza el HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Elimina etiquetas no deseadas (scripts, estilos, menús, imágenes, etc.)
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "img", "svg"]):
        tag.decompose()

    # Extrae el texto visible, separando por saltos de línea
    text = soup.get_text(separator="\n")

    # Limpia líneas vacías o con solo espacios
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Devuelve las primeras 1000 líneas para evitar textos excesivamente largos
    return "\n\n".join(lines[:1000])

def compile_pages(selected_links, session=None, rate_limit=0.6):
    """
    Descarga y limpia el contenido de un conjunto de enlaces seleccionados.
    """
    pages = {}
    from .scraping import fetch, extract_links  # Import local para evitar dependencias circulares

    # Recorre cada enlace seleccionado
    for item in selected_links.get("links", []):
        url = item["url"]              # URL de la página
        typ = item.get("type", "other")  # Tipo de página (si se define)

        try:
            # Descarga el contenido HTML de la página
            _, html = fetch(url, session=session)

            # Limpia el HTML para quedarse solo con el texto relevante
            txt = clean_text_from_html(html)

            # Guarda el resultado en el diccionario 'pages'
            pages[typ] = {"url": url, "text": txt}

        except Exception as e:
            # Registra un error si falla la descarga o limpieza
            logger.error("Fallo al compilar %s: %s", url, e)

    # Devuelve todas las páginas procesadas
    return pages
