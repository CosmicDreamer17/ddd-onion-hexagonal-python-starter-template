import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from integration_management.infrastructure.api import create_integration_management_router
from integration_management.infrastructure.unit_of_work import (
    SqlAlchemyIntegrationManagementUnitOfWork,
)


@pytest.fixture
def client(engine):
    app = FastAPI()
    app.include_router(
        create_integration_management_router(
            lambda: SqlAlchemyIntegrationManagementUnitOfWork(engine)
        )
    )
    return TestClient(app)


class TestCreateIntegrationJob:
    def test_returns_201_with_id(self, client):
        response = client.post("/jobs", json={"source": "system-a", "payload": "data"})
        assert response.status_code == 201
        assert "id" in response.json()


class TestGetIntegrationJob:
    def test_returns_200_with_job(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]

        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["source"] == "system-a"
        assert data["status"] == "queued"
        assert data["error_message"] is None

    def test_returns_404_for_nonexistent_job(self, client):
        response = client.get(f"/jobs/{uuid.uuid4()}")
        assert response.status_code == 404


class TestStartProcessingJob:
    def test_returns_204_on_success(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]

        response = client.post(f"/jobs/{job_id}/start-processing")
        assert response.status_code == 204

    def test_returns_409_for_invalid_transition(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]
        client.post(f"/jobs/{job_id}/start-processing")

        response = client.post(f"/jobs/{job_id}/start-processing")
        assert response.status_code == 409

    def test_returns_404_for_nonexistent_job(self, client):
        response = client.post(f"/jobs/{uuid.uuid4()}/start-processing")
        assert response.status_code == 404


class TestDeliverJob:
    def test_returns_204_on_success(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]
        client.post(f"/jobs/{job_id}/start-processing")

        response = client.post(f"/jobs/{job_id}/deliver")
        assert response.status_code == 204

    def test_returns_409_for_invalid_transition(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]

        response = client.post(f"/jobs/{job_id}/deliver")
        assert response.status_code == 409


class TestFailJob:
    def test_returns_204_on_success(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]
        client.post(f"/jobs/{job_id}/start-processing")

        response = client.post(f"/jobs/{job_id}/fail", json={"reason": "Timeout"})
        assert response.status_code == 204

    def test_returns_409_for_invalid_transition(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]

        response = client.post(f"/jobs/{job_id}/fail", json={"reason": "Error"})
        assert response.status_code == 409

    def test_returns_404_for_nonexistent_job(self, client):
        response = client.post(f"/jobs/{uuid.uuid4()}/fail", json={"reason": "Error"})
        assert response.status_code == 404


class TestRetryJob:
    def test_returns_204_on_success(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]
        client.post(f"/jobs/{job_id}/start-processing")
        client.post(f"/jobs/{job_id}/fail", json={"reason": "Timeout"})

        response = client.post(f"/jobs/{job_id}/retry")
        assert response.status_code == 204

    def test_returns_409_for_invalid_transition(self, client):
        job_id = client.post(
            "/jobs", json={"source": "system-a", "payload": "data"}
        ).json()["id"]

        response = client.post(f"/jobs/{job_id}/retry")
        assert response.status_code == 409

    def test_returns_404_for_nonexistent_job(self, client):
        response = client.post(f"/jobs/{uuid.uuid4()}/retry")
        assert response.status_code == 404
