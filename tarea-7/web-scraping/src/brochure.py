# src/brochure.py
import os
import json
from .link_selector import call_ollama, MOCK_MODE, OLLAMA_MODEL
from .utils import save_text, slug
import logging
from markdown import markdown
# weasyprint optional
try:
    from weasyprint import HTML
    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False

logger = logging.getLogger(__name__)
BROCHURE_PROMPT_TEMPLATE = open("prompts/brochure_system.md","r",encoding="utf-8").read()

def generate_brochure(company_name: str, pages: dict, tone: str="formal") -> str:
    # construye prompt con el contenido de las páginas (texto consolidado)
    content_parts = []
    for k,v in pages.items():
        content_parts.append(f"=== {k} ({v.get('url')}) ===\n{v.get('text')[:4000]}")
    content_blob = "\n\n".join(content_parts)
    prompt = BROCHURE_PROMPT_TEMPLATE.format(company=company_name, tone=tone, pages=content_blob)
    raw = call_ollama(prompt)
    # Si es mock, call_ollama devolverá JSON/markdown simulado
    # asumimos que la respuesta es markdown
    md = raw
    # Guardar
    filename = f"outputs/{slug(company_name)}_brochure.md"
    save_text(filename, md)
    logger.info("Brochure saved to %s", filename)
    return filename

def export_pdf(md_path: str, html_out: str=None, pdf_out: str=None):
    text = open(md_path, "r", encoding="utf-8").read()
    html = markdown(text)
    html_out = html_out or md_path.replace(".md",".html")
    open(html_out,"w",encoding="utf-8").write(html)
    if HAVE_WEASY and pdf_out:
        HTML(string=html).write_pdf(pdf_out)
