import uuid

import pytest
from fastapi.testclient import TestClient

from shared.infrastructure.app import create_app


@pytest.fixture
def client(engine):
    app = create_app(engine)
    return TestClient(app)


class TestListIntegrationJobs:
    def test_empty_list(self, client):
        response = client.get("/integration-jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_lists_created_jobs(self, client):
        client.post("/integration-jobs", json={"source": "a", "payload": "p1"})
        client.post("/integration-jobs", json={"source": "b", "payload": "p2"})

        response = client.get("/integration-jobs")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filters_by_status(self, client):
        resp = client.post("/integration-jobs", json={"source": "a", "payload": "p"})
        job_id = resp.json()["id"]
        client.post("/integration-jobs", json={"source": "b", "payload": "p"})
        client.post(f"/integration-jobs/{job_id}/start")

        processing = client.get("/integration-jobs?status=processing")
        assert len(processing.json()) == 1


class TestGetIntegrationJob:
    def test_returns_job(self, client):
        resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = resp.json()["id"]

        response = client.get(f"/integration-jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["source"] == "api"
        assert response.json()["status"] == "queued"

    def test_returns_404_for_nonexistent(self, client):
        response = client.get(f"/integration-jobs/{uuid.uuid4()}")
        assert response.status_code == 404


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
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        response = client.post(f"/integration-jobs/{job_id}/start")
        assert response.status_code == 204

        response = client.post(f"/integration-jobs/{job_id}/deliver")
        assert response.status_code == 204

        # Verify final state via GET
        get_resp = client.get(f"/integration-jobs/{job_id}")
        assert get_resp.json()["status"] == "delivered"

    def test_fail_and_retry(self, client):
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        client.post(f"/integration-jobs/{job_id}/start")

        response = client.post(
            f"/integration-jobs/{job_id}/fail", json={"reason": "Timeout"}
        )
        assert response.status_code == 204

        response = client.post(f"/integration-jobs/{job_id}/retry")
        assert response.status_code == 204

    def test_invalid_transition_returns_409(self, client):
        create_resp = client.post(
            "/integration-jobs", json={"source": "api", "payload": "data"}
        )
        job_id = create_resp.json()["id"]

        response = client.post(f"/integration-jobs/{job_id}/deliver")
        assert response.status_code == 409

    def test_nonexistent_returns_404(self, client):
        response = client.post(f"/integration-jobs/{uuid.uuid4()}/start")
        assert response.status_code == 404
