# src/cli.py
import argparse
import logging
import requests
from src.scraping import scrape_and_extract
from src.link_selector import select_relevant_links
from src.compiler import compile_pages
from src.brochure import generate_brochure, export_pdf
from src.utils import slug, save_text

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--tone", choices=["formal","humoristic"], default="formal")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()

    html_main, links = scrape_and_extract(args.url)
    selected = select_relevant_links(args.url, links)
    pages = compile_pages(selected)
    md_file = generate_brochure(args.company, pages, tone=args.tone)
    if args.pdf:
        export_pdf(md_file, pdf_out=md_file.replace(".md",".pdf"))
    print("Brochure:", md_file)

if __name__ == "__main__":
    main()
