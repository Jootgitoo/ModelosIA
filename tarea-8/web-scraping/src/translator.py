# src/translator.py
import logging
from .link_selector import call_ollama
from .utils import save_text, slug, sanitize_markdown

logger = logging.getLogger(__name__)

# Carga el prompt del traductor
TRANSLATOR_PROMPT = open(
    "prompts/translator_system.md",
    "r",
    encoding="utf-8"
).read()


def translate_brochure(company_name: str, markdown_text: str, lang: str):
    """
    Traduce un texto Markdown al idioma indicado usando LLM3.
    
    Parámetros:
        - company_name: nombre de la empresa (para nombrar salida)
        - markdown_text: el folleto en español (Markdown)
        - lang: idioma destino ('fr', 'de', 'en', 'it', 'pt', etc.)
    """

    logger.info("Traduciendo folleto a idioma '%s'...", lang)

    # Preparamos el prompt sustituible
    prompt = TRANSLATOR_PROMPT.format(
        lang=lang,
        content=markdown_text
    )

    # Llama al modelo
    raw = call_ollama(prompt)

    # Limpiamos y validamos el markdown
    translated_md = sanitize_markdown(raw)

    # Guardar la traducción
    filename = f"outputs/{slug(company_name)}_brochure_{lang}.md"
    save_text(filename, translated_md)

    logger.info("Folleto traducido guardado en %s", filename)

    return filename, translated_md
