import pytest
import requests
from wakeonlanservice import create_app
from wakeonlanservice.blueprints.status import check_url_status
import os
from unittest.mock import patch

@pytest.fixture
def app(scope="function"):
    """Create and configure a Flask app for testing."""
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key"  # Set a fixed secret key for testing
    })
    # Set environment variables for testing
    os.environ["MAC_ADDRESS"] = "00:11:22:33:44:55"
    os.environ["URL"] = "http://example.com"
    return app

@pytest.fixture
def client(app):
    return app.test_client()

class TestIndex:
    def test_index(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Loading, please wait..." in response.data

class TestCheckUrlStatus:
    def test_check_url_status_success(self, monkeypatch):
        def mock_get(*args, **kwargs):
            class MockResponse:
                status_code = 200
            return MockResponse()
        monkeypatch.setattr("requests.get", mock_get)
        assert check_url_status("https://example.com") is True

    def test_check_url_status_failure(self, monkeypatch):
        def mock_get(*args, **kwargs):
            raise requests.RequestException("Request failed")
        monkeypatch.setattr("requests.get", mock_get)
        assert check_url_status("https://example.com") is False

class TestMultipleAppInstances:
    def test_multiple_app_instances_attempts(self):
        # Create two separate app instances with their own clients
        app1 = create_app({"TESTING": True, "SECRET_KEY": "test_key_1"})
        app2 = create_app({"TESTING": True, "SECRET_KEY": "test_key_2"})
        
        client1 = app1.test_client()
        client2 = app2.test_client()
        
        # Set up mocking for check_url_status and send_magic_packet
        with patch("wakeonlanservice.blueprints.status.check_url_status", return_value=False):
            with patch("wakeonlanservice.blueprints.status.send_magic_packet"):
                # Initialize sessions
                client1.get("/")
                client2.get("/")
                
                # First client makes 3 attempts
                for _ in range(3):
                    client1.get("/check_url")
                
                # Second client makes 1 attempt
                client2.get("/check_url")
                
                # Get current state
                response1 = client1.get("/check_url")
                response2 = client2.get("/check_url")
                
                # Verify each client has its own separate attempt count
                assert response1.get_json()["attempts"] == 4
                assert response2.get_json()["attempts"] == 2

class TestCheckUrl:
    def test_check_url_available(self, monkeypatch, client):
        with patch("wakeonlanservice.blueprints.status.check_url_status", return_value=True):
            with patch("wakeonlanservice.blueprints.status.send_magic_packet"):
                # Initialize session
                client.get("/")
                
                # Check URL
                response = client.get("/check_url")
                assert response.status_code == 200
                data = response.get_json()
                assert data["status"] == "available"
                assert data["attempts"] == 1

    def test_check_url_unavailable(self, monkeypatch, client):
        with patch("wakeonlanservice.blueprints.status.check_url_status", return_value=False):
            with patch("wakeonlanservice.blueprints.status.send_magic_packet"):
                # Initialize session
                client.get("/")
                
                # Check URL
                response = client.get("/check_url")
                assert response.status_code == 200
                data = response.get_json()
                assert data["status"] == "unavailable"
                assert data["attempts"] == 1

    def test_check_url_error(self, monkeypatch, client):
        with patch("wakeonlanservice.blueprints.status.check_url_status", return_value=False):
            with patch("wakeonlanservice.blueprints.status.send_magic_packet"):
                # Initialize session
                client.get("/")
                
                # Make 10 attempts
                for _ in range(10):
                    client.get("/check_url")
                
                # Check status after threshold
                response = client.get("/check_url")
                assert response.status_code == 200
                data = response.get_json()
                assert data["status"] == "error"
                assert data["attempts"] == 11

class TestHealthCheck:
    def test_healthcheck(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"