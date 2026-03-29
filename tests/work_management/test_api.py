import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from work_management.infrastructure.api import create_work_management_router
from work_management.infrastructure.unit_of_work import SqlAlchemyWorkManagementUnitOfWork


@pytest.fixture
def client(engine):
    app = FastAPI()
    app.include_router(
        create_work_management_router(lambda: SqlAlchemyWorkManagementUnitOfWork(engine))
    )
    return TestClient(app)


class TestCreateWorkItem:
    def test_returns_201_with_id(self, client):
        response = client.post("/work-items", json={"title": "Test Task"})
        assert response.status_code == 201
        assert "id" in response.json()


class TestGetWorkItem:
    def test_returns_200_with_work_item(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]

        response = client.get(f"/work-items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"
        assert data["assigned_to"] is None

    def test_returns_404_for_nonexistent_item(self, client):
        response = client.get(f"/work-items/{uuid.uuid4()}")
        assert response.status_code == 404


class TestAssignWorkItem:
    def test_returns_204_on_success(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]

        response = client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "owner@example.com"},
        )
        assert response.status_code == 204

    def test_returns_422_for_invalid_email(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]

        response = client.post(
            f"/work-items/{item_id}/assign",
            json={"owner_email": "not-an-email"},
        )
        assert response.status_code == 422

    def test_returns_404_for_nonexistent_item(self, client):
        response = client.post(
            f"/work-items/{uuid.uuid4()}/assign",
            json={"owner_email": "owner@example.com"},
        )
        assert response.status_code == 404


class TestActivateWorkItem:
    def test_returns_204_on_success(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]
        client.post(
            f"/work-items/{item_id}/assign", json={"owner_email": "owner@example.com"}
        )

        response = client.post(f"/work-items/{item_id}/activate")
        assert response.status_code == 204

    def test_returns_422_when_no_owner_assigned(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]

        response = client.post(f"/work-items/{item_id}/activate")
        assert response.status_code == 422

    def test_returns_409_for_invalid_state_transition(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]
        client.post(
            f"/work-items/{item_id}/assign", json={"owner_email": "owner@example.com"}
        )
        client.post(f"/work-items/{item_id}/activate")

        response = client.post(f"/work-items/{item_id}/activate")
        assert response.status_code == 409

    def test_returns_404_for_nonexistent_item(self, client):
        response = client.post(f"/work-items/{uuid.uuid4()}/activate")
        assert response.status_code == 404


class TestCompleteWorkItem:
    def test_returns_204_on_success(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]
        client.post(
            f"/work-items/{item_id}/assign", json={"owner_email": "owner@example.com"}
        )
        client.post(f"/work-items/{item_id}/activate")

        response = client.post(f"/work-items/{item_id}/complete")
        assert response.status_code == 204

    def test_returns_409_for_invalid_state_transition(self, client):
        item_id = client.post("/work-items", json={"title": "Test Task"}).json()["id"]

        response = client.post(f"/work-items/{item_id}/complete")
        assert response.status_code == 409

    def test_returns_404_for_nonexistent_item(self, client):
        response = client.post(f"/work-items/{uuid.uuid4()}/complete")
        assert response.status_code == 404
