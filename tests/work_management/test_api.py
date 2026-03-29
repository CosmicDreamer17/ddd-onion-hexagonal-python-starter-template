import uuid

import pytest
from fastapi.testclient import TestClient

from shared.infrastructure.app import create_app


@pytest.fixture
def client(engine):
    app = create_app(engine)
    return TestClient(app)


class TestCreateWorkItem:
    def test_creates_item(self, client):
        response = client.post("/work-items", json={"title": "New Task"})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        uuid.UUID(data["id"])  # validates UUID format

    def test_rejects_missing_title(self, client):
        response = client.post("/work-items", json={})
        assert response.status_code == 422


class TestAssignWorkItem:
    def test_assigns_owner(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]

        response = client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "alice@example.com"},
        )
        assert response.status_code == 204

    def test_rejects_invalid_email(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]

        response = client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "invalid"},
        )
        assert response.status_code == 422

    def test_returns_404_for_nonexistent(self, client):
        response = client.post(
            f"/work-items/{uuid.uuid4()}/assign",
            json={"owner_email": "alice@example.com"},
        )
        assert response.status_code == 404


class TestActivateWorkItem:
    def test_activates_assigned_item(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]
        client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "alice@example.com"},
        )

        response = client.post(f"/work-items/{item_id}/activate")
        assert response.status_code == 204

    def test_returns_409_without_owner(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]

        response = client.post(f"/work-items/{item_id}/activate")
        assert response.status_code == 409


class TestCompleteWorkItem:
    def test_completes_active_item(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]
        client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "alice@example.com"},
        )
        client.post(f"/work-items/{item_id}/activate")

        response = client.post(f"/work-items/{item_id}/complete")
        assert response.status_code == 204

    def test_returns_409_from_pending(self, client):
        create_resp = client.post("/work-items", json={"title": "Task"})
        item_id = create_resp.json()["id"]

        response = client.post(f"/work-items/{item_id}/complete")
        assert response.status_code == 409
