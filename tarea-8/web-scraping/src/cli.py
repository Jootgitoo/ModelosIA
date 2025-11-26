# src/cli.py
import argparse
import logging
import requests
from src.scraping import scrape_and_extract
from src.link_selector import select_relevant_links
from src.compiler import compile_pages
from src.brochure import generate_brochure, export_pdf
from src.utils import slug, save_text

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

# Si se ejecuta directamente desde la terminal, inicia el proceso
if __name__ == "__main__":
    main()


##
# Ejemplo de uso por terminal:
# python src/cli.py --company "Python Software Foundation" --url "https://www.python.org"
##
