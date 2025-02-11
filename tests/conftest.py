import pytest

# This fixture will be automatically applied to all tests
# It sets the required environment variables for the tests
@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("MAC_ADDRESS", "18:C0:4D:07:5B:2D")
    monkeypatch.setenv("URL", "https://example.com")