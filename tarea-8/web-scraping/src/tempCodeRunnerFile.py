
import argparse
import logging
import time
import requests

from src.scraping import scrape_and_extract, fetch, extract_text_snippet
from src.link_selector import select_relevant_links
from src.compiler import compile_pages
from src.brochure import generate_brochure
from src.translator import translate_brochure

<<<<<<< Updated upstream
# Configuración básica del nivel de logs (INFO)
logging.basicConfig(level=logging.INFO)

def main():
    """
    Punto de entrada principal de la aplicación por línea de comandos.
    Permite generar un folleto a partir de la web de una empresa.
    """
    # Define y configura los argumentos que se pueden pasar al script
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True, help="Nombre de la empresa")
    parser.add_argument("--url", required=True, help="URL principal de la empresa")
    parser.add_argument("--tone", choices=["formal", "humoristic"], default="formal", help="Tono del folleto generado")
    parser.add_argument("--pdf", action="store_true", help="Exportar también el folleto en PDF")
    args = parser.parse_args()

    # Paso 1: Descarga la página principal y extrae sus enlaces
    html_main, links = scrape_and_extract(args.url)

    # Paso 2: Usa el modelo de IA para seleccionar los enlaces más relevantes
    selected = select_relevant_links(args.url, links)

    # Paso 3: Compila el contenido de las páginas seleccionadas
    pages = compile_pages(selected)

    # Paso 4: Genera el folleto en formato Markdown
    md_file = generate_brochure(args.company, pages, tone=args.tone)

    # Paso 5 (opcional): Exporta también a PDF si se indica
    if args.pdf:
        export_pdf(md_file, pdf_out=md_file.replace(".md", ".pdf"))

    # Muestra el resultado por consola
    print("Brochure:", md_file)
=======
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Generador completo de folleto corporativo (Scraping + LLM1 + LLM2 + LLM3)")

    parser.add_argument("url", type=str, help="URL principal de la empresa (landing)")
    parser.add_argument("company", type=str, help="Nombre de la empresa")
    parser.add_argument("--tone", type=str, default="formal", help="Tono del folleto (formal, tecnico, divertido)")
    parser.add_argument("--lang", type=str, default=None, help="Idioma opcional para traducir el folleto (ej: en, fr, de, it)")

    args = parser.parse_args()

    base_url = args.url
    company_name = args.company
    tone = args.tone
    lang = args.lang

    logger.info("1) SCRAPING raíz: %s", base_url)
    html, links, snippet = scrape_and_extract(base_url)

    logger.info("Se detectaron %d enlaces en la landing", len(links))

    # Creamos sesión HTTP
    session = requests.Session()

    # 2) Construimos items con snippet individual
    logger.info("2) Descargando cada enlace para generar snippets...")
    items = []
    for link in links:
        # Evitar enlaces externos
        if not link.startswith(base_url):
            continue

        try:
            _, child_html = fetch(link, session=session)
            child_snippet = extract_text_snippet(child_html)

            items.append({
                "url": link,
                "snippet": child_snippet
            })

            time.sleep(0.6)  # rate limit

        except Exception as e:
            logger.warning("No se pudo procesar enlace %s: %s", link, e)

    logger.info("Snippets generados para %d enlaces", len(items))

    # 3) LLM1 selección
    logger.info("3) Seleccionando enlaces relevantes con LLM1...")
    selected = select_relevant_links(base_url, items)

    logger.info("LLM1 seleccionó %d enlaces con score >= 60", len(selected.get("links", [])))

    # 4) Compiler
    logger.info("4) Compilando contenido con compiler...")
    compiled_text = compile_pages(selected, session=session)

    # 5) LLM2 generar folleto
    logger.info("5) Generando folleto (LLM2)...")
    brochure_path, brochure_md = generate_brochure(company_name, compiled_text, tone)

    print(f"\nFolleto generado: {brochure_path}\n")

    # 6) LLM3 traducción opcional
    if lang:
        logger.info("6) Traduciendo folleto (LLM3) a '%s'...", lang)
        translated_path, translated_md = translate_brochure(company_name, brochure_md, lang)
        print(f"Folleto traducido: {translated_path}")

>>>>>>> Stashed changes

# Si se ejecuta directamente desde la terminal, inicia el proceso
if __name__ == "__main__":
    main()


##
# Ejemplo de uso por terminal:
# python src/cli.py --company "Python Software Foundation" --url "https://www.python.org"
##
