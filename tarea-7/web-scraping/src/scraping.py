# src/scraping.py
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from urllib import robotparser
from pathlib import Path
from typing import List, Tuple
from .utils import get_user_agent, rate_limit_sleep

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10

def can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        logger.info("No robots.txt accesible (%s): %s", robots_url, e)
        return True  # si no se puede leer, optamos por intentar con precaución
    return rp.can_fetch(get_user_agent(), url)

def fetch(url: str, session: requests.Session = None) -> Tuple[int,str]:
    session = session or requests.Session()
    headers = {"User-Agent": get_user_agent()}
    try:
        resp = session.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        logger.info("Fetched %s (%d)", url, resp.status_code)
        return resp.status_code, resp.text
    except requests.RequestException as e:
        logger.error("Error fetching %s: %s", url, e)
        raise

def extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    # remueve tags que no aportan
    for tag in soup(["script","style","noscript", "svg", "img", "input", "button", "meta"]):
        tag.decompose()
    links = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        if href:
            abs_url = urljoin(base_url, href)
            links.add(abs_url)
    return list(links)

def scrape_and_extract(url: str, session: requests.Session = None, rate_limit: float = 0.6):
    if not can_fetch(url):
        raise PermissionError(f"Scraping blocked by robots.txt: {url}")
    session = session or requests.Session()
    status, html = fetch(url, session=session)
    time.sleep(rate_limit_sleep(rate_limit))
    links = extract_links(html, base_url=url)
    return html, links
