import pytest
import requests
from wakeonlanservice import create_app
from wakeonlanservice.blueprints.status import check_url_status

@pytest.fixture
def app(scope="function"):
    app = create_app({"TESTING": True})
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
        app1 = create_app({"TESTING": True})
        app2 = create_app({"TESTING": True})
        
        client1 = app1.test_client()
        client1.get("/check_url")
        assert app1.config["ATTEMPTS"] == 1

        client2 = app2.test_client()
        client2.get("/check_url")
        assert app2.config["ATTEMPTS"] == 1

class TestCheckUrl:
    def test_check_url_available(self, monkeypatch, client):
        def mock_get(*args, **kwargs):
            class MockResponse:
                status_code = 200
            return MockResponse()
        monkeypatch.setattr("requests.get", mock_get)
        
        response = client.get("/check_url")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "available"
        assert data["attempts"] == 1

    def test_check_url_unavailable(self, monkeypatch, client):
        def mock_get(*args, **kwargs):
            class MockResponse:
                status_code = 404
            return MockResponse()
        monkeypatch.setattr("requests.get", mock_get)
        
        response = client.get("/check_url")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "unavailable"
        assert data["attempts"] == 1

    def test_check_url_error(self, monkeypatch, client):
        def mock_get(*args, **kwargs):
            class MockResponse:
                status_code = 404
            return MockResponse()
        monkeypatch.setattr("requests.get", mock_get)
        
        for _ in range(10):
            client.get("/check_url")
        
        response = client.get("/check_url")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "error"
        assert data["attempts"] == 11