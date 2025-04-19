import pytest
from flask import Flask
from wakeonlanservice import create_app, validate_env_variables

class TestCreateApp:
    def test_app_creation(self):
        app = create_app({"TESTING": True})
        
        assert isinstance(app, Flask)
        assert app is not None
        assert app.config["TESTING"] is True

    def test_create_app_prod(self, monkeypatch):
        # Set FLASK_DEBUG environment variable to '0' (False)
        monkeypatch.setenv("FLASK_DEBUG", "0")
        app = create_app()
        
        assert isinstance(app, Flask)
        assert app.debug is False
        assert "SECRET_KEY" in app.config
        assert app.config["SECRET_KEY"] is not None

    def test_create_app_debug(self, monkeypatch):
        # Set FLASK_DEBUG environment variable to '1' (True)
        monkeypatch.setenv("FLASK_DEBUG", "1")
        app = create_app()
        
        assert isinstance(app, Flask)
        assert app.debug is True
        assert "SECRET_KEY" in app.config
        assert app.config["SECRET_KEY"] is not None

class TestValidateEnvVariables:
    def test_validate_env_variables_valid(self, monkeypatch):
        monkeypatch.setenv("MAC_ADDRESS", "18:C0:4D:07:5B:2D")
        monkeypatch.setenv("URL", "https://example.com")
        try:
            validate_env_variables()
        except ValueError:
            pytest.fail("validate_env_variables() raised ValueError unexpectedly!")

    def test_validate_env_variables_invalid_mac(self, monkeypatch):
        monkeypatch.setenv("MAC_ADDRESS", "invalid_mac")
        monkeypatch.setenv("URL", "https://example.com")
        with pytest.raises(ValueError, match="Invalid or missing MAC_ADDRESS environment variable"):
            validate_env_variables()

    def test_validate_env_variables_invalid_url(self, monkeypatch):
        monkeypatch.setenv("MAC_ADDRESS", "18:C0:4D:07:5B:2D")
        monkeypatch.setenv("URL", "invalid_url")
        with pytest.raises(ValueError, match="Invalid or missing URL environment variable"):
            validate_env_variables()