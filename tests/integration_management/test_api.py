import uuid

import pytest
from fastapi.testclient import TestClient

from shared.infrastructure.app import create_app


@pytest.fixture
def client(engine):
    app = create_app(engine)
    return TestClient(app)


class TestCreateIntegrationJob:
    def test_creates_job(self, client):
        response = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        uuid.UUID(data["id"])


class TestIntegrationJobLifecycle:
    def test_full_lifecycle(self, client):
        # Create
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        # Start processing
        response = client.post(f"/integration-jobs/{job_id}/start")
        assert response.status_code == 204

        # Deliver
        response = client.post(f"/integration-jobs/{job_id}/deliver")
        assert response.status_code == 204

    def test_fail_and_retry(self, client):
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        client.post(f"/integration-jobs/{job_id}/start")

        # Fail
        response = client.post(
            f"/integration-jobs/{job_id}/fail", json={"reason": "Timeout"}
        )
        assert response.status_code == 204

        # Retry
        response = client.post(f"/integration-jobs/{job_id}/retry")
        assert response.status_code == 204

    def test_invalid_transition_returns_409(self, client):
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        # Try to deliver before starting
        response = client.post(f"/integration-jobs/{job_id}/deliver")
        assert response.status_code == 409

    def test_nonexistent_returns_404(self, client):
        response = client.post(f"/integration-jobs/{uuid.uuid4()}/start")
        assert response.status_code == 404
