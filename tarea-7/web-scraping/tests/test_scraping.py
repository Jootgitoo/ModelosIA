from src.scraping import extract_links

def test_extract_links_relative():
    """
    Prueba unitaria para la función extract_links del módulo scraping.
    Verifica que los enlaces relativos se convierten en absolutos correctamente.
    """
    # HTML de ejemplo con un enlace relativo y otro absoluto
    html = '<html><body><a href="/about">About</a><a href="https://ex.com/careers">Careers</a></body></html>'
    
    # Llama a la función indicando la URL base
    links = extract_links(html, "https://example.com")
    
    # Comprueba que el enlace relativo se convierte correctamente en absoluto
    assert "https://example.com/about" in links
    
    # Comprueba que el enlace absoluto se mantiene sin cambios
    assert "https://ex.com/careers" in links
