from src.scraping import extract_links

def test_extract_links_relative():
    html = '<html><body><a href="/about">About</a><a href="https://ex.com/careers">Careers</a></body></html>'
    links = extract_links(html,"https://example.com")
    assert "https://example.com/about" in links
    assert "https://ex.com/careers" in links
