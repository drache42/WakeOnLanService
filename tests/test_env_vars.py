import os

# This verifies that the required environment variables are set for other tests
def test_env_vars():
    assert os.getenv("MAC_ADDRESS") == "18:C0:4D:07:5B:2D"
    assert os.getenv("URL") == "https://example.com"