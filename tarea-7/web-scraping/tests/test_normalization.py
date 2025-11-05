from src.utils import slug
def test_slug():
    assert slug("My Company, Inc.") == "my-company-inc"
