# src/brochure.py
import os
import json
import logging
from .link_selector import call_ollama
from .utils import save_text, slug, sanitize_markdown
from markdown import markdown

try:
    from weasyprint import HTML
    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False

logger = logging.getLogger(__name__)

# Cargamos template del prompt de sistema
BROCHURE_SYSTEM_PROMPT = open(
    "prompts/brochure_system.md", "r", encoding="utf-8"
).read()


def generate_brochure(company_name: str, compiled_text: str, tone: str = "formal"):
    """
    Genera un folleto en formato Markdown usando LLM2.
    Recibe:
        - company_name: nombre de la empresa
        - compiled_text: texto unificado de compiler.py
        - tone: formal | divertido | técnico
    Devuelve:
        - ruta del archivo .md generado
    """

    # Construimos el prompt final
    prompt = BROCHURE_SYSTEM_PROMPT.format(
        company=company_name,
        tone=tone,
        content=compiled_text[:16000]  # límite seguro
    )

    logger.info("Generando folleto para %s...", company_name)

    # Llamada al modelo
    raw = call_ollama(prompt)

    # El LLM devuelve markdown directamente
    md = sanitize_markdown(raw)

    # Guardamos en archivo
    filename = f"outputs/{slug(company_name)}_brochure.md"
    save_text(filename, md)

    logger.info("Brochure guardado en %s", filename)

    return filename, md


def export_pdf(md_path: str, html_out: str = None, pdf_out: str = None):
    """
    Convierte markdown → HTML → PDF (si weasyprint disponible)
    """
    text = open(md_path, "r", encoding="utf-8").read()

    html = markdown(text)
    html_out = html_out or md_path.replace(".md", ".html")

    open(html_out, "w", encoding="utf-8").write(html)

    if HAVE_WEASY and pdf_out:
        HTML(string=html).write_pdf(pdf_out)
        logger.info("PDF generado en %s", pdf_out)

def sanitize_markdown(md: str) -> str:
    """
    Limpia respuestas de LLM:
    - elimina texto fuera de markdown
    - recorta espacios extra
    - evita encabezados duplicados
    """
    lines = md.splitlines()
    clean = [ln.rstrip() for ln in lines]
    return "\n".join(clean).strip()
