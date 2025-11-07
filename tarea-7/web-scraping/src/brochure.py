# src/brochure.py
import os
import json
from .link_selector import call_ollama, MOCK_MODE, OLLAMA_MODEL
from .utils import save_text, slug
import logging
from markdown import markdown

# Intentamos importar weasyprint (para generar PDFs)
try:
    from weasyprint import HTML
    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False

# Configuración del logger
logger = logging.getLogger(__name__)

# Cargamos la plantilla del prompt para generar folletos
BROCHURE_PROMPT_TEMPLATE = open("prompts/brochure_system.md","r",encoding="utf-8").read()

def generate_brochure(company_name: str, pages: dict, tone: str="formal") -> str:
    """
    Genera un folleto en formato Markdown usando un modelo de lenguaje.
    """
    # Construye el contenido del prompt con las páginas de la empresa
    content_parts = []
    for k,v in pages.items():
        # Añade título, URL y texto limitado a 4000 caracteres
        content_parts.append(f"=== {k} ({v.get('url')}) ===\n{v.get('text')[:4000]}")
    
    # Une todo el contenido de las páginas
    content_blob = "\n\n".join(content_parts)
    # Rellena la plantilla con los datos de la empresa
    prompt = BROCHURE_PROMPT_TEMPLATE.format(company=company_name, tone=tone, pages=content_blob)
    
    # Llama al modelo (IA) para generar el texto del folleto
    raw = call_ollama(prompt)
    
    # Asumimos que la respuesta está en formato Markdown
    md = raw
    
    # Guarda el folleto generado en un archivo .md
    filename = f"outputs/{slug(company_name)}_brochure.md"
    save_text(filename, md)
    logger.info("Brochure saved to %s", filename)
    
    return filename

def export_pdf(md_path: str, html_out: str=None, pdf_out: str=None):
    """
    Convierte un archivo Markdown en HTML y opcionalmente en PDF.
    """
    # Lee el archivo Markdown
    text = open(md_path, "r", encoding="utf-8").read()
    # Convierte Markdown a HTML
    html = markdown(text)
    # Genera el nombre de salida del archivo HTML
    html_out = html_out or md_path.replace(".md",".html")
    # Guarda el HTML generado
    open(html_out,"w",encoding="utf-8").write(html)
    
    # Si weasyprint está disponible, genera también el PDF
    if HAVE_WEASY and pdf_out:
        HTML(string=html).write_pdf(pdf_out)
