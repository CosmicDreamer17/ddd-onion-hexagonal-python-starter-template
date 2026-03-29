import uuid

import pytest
from fastapi.testclient import TestClient

from shared.infrastructure.app import create_app


@pytest.fixture
def client(engine):
    app = create_app(engine)
    return TestClient(app)


class TestHealthCheck:
    def test_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestListWorkItems:
    def test_empty_list(self, client):
        response = client.get("/work-items")
        assert response.status_code == 200
        assert response.json() == []

    def test_lists_created_items(self, client):
        client.post("/work-items", json={"title": "Task 1"})
        client.post("/work-items", json={"title": "Task 2"})

        response = client.get("/work-items")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filters_by_status(self, client):
        resp = client.post("/work-items", json={"title": "Task 1"})
        item_id = resp.json()["id"]
        client.post("/work-items", json={"title": "Task 2"})
        client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "a@b.com"},
        )
        client.post(f"/work-items/{item_id}/activate")

        active = client.get("/work-items?status=active")
        assert len(active.json()) == 1
        assert active.json()[0]["status"] == "active"


class TestGetWorkItem:
    def test_returns_item(self, client):
        resp = client.post("/work-items", json={"title": "My Task"})
        item_id = resp.json()["id"]

        response = client.get(f"/work-items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Task"
        assert data["status"] == "pending"

    def test_returns_404_for_nonexistent(self, client):
        response = client.get(f"/work-items/{uuid.uuid4()}")
        assert response.status_code == 404


class TestCreateWorkItem:
    def test_creates_item(self, client):
        response = client.post("/work-items", json={"title": "New Task"})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        uuid.UUID(data["id"])

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
