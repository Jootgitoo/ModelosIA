# src/compiler.py
from bs4 import BeautifulSoup
from .scraping import fetch
from .utils import slug
import logging

logger = logging.getLogger(__name__)

def clean_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header","form","img","svg"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # normalización simple: colapsar lineas en blanco
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n\n".join(lines[:1000])  # limit to avoid huge prompts

def compile_pages(selected_links, session=None, rate_limit=0.6):
    pages = {}
    from .scraping import fetch, extract_links
    for item in selected_links.get("links", []):
        url = item["url"]
        typ = item.get("type", "other")
        try:
            _, html = fetch(url, session=session)
            txt = clean_text_from_html(html)
            pages[typ] = {"url": url, "text": txt}
        except Exception as e:
            logger.error("Fallo al compilar %s: %s", url, e)
    return pages
