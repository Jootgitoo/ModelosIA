from src.utils import slug

def test_slug():
    """
    Prueba unitaria para la función slug del módulo utils.
    """
    # Comprueba que el texto se convierte correctamente en un slug (formato URL/archivo seguro)
    assert slug("My Company, Inc.") == "my-company-inc"
