import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .main import app
from .dependencies import get_current_db
from .models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_current_db] = override_get_db


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def test_user():
    return {"username": "test", "password": "test1234"}


client = TestClient(app)


def test_create_user(test_db):
    response = client.post(
        "/users/signup",
        json={"username": "test", "password": "test1234", "email": "test@test.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    assert data["email"] == "test@test.com"


def test_login_user(test_user):
    response = client.post(
        "/users/login",
        data=test_user,
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    return data["access_token"]


def test_create_appointment(test_db, test_user):
    token = test_login_user(test_user)
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["start"] == "2022-01-01T10:00:00"
    assert data["end"] == "2022-01-01T11:00:00"
    assert data["organization_id"] == 1


def test_create_appointment_conflict(test_db, test_user):
    token = test_login_user(test_user)
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
    )
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


def test_read_appointments(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/appointments/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_read_appointment_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/appointments/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_update_appointment_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.put(
        "/appointments/999",
        json={"start": "2022-01-01T12:00:00", "end": "2022-01-01T13:00:00", "organization_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_delete_appointment_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.delete("/appointments/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_create_organization(test_db, test_user):
    token = test_login_user(test_user)
    response = client.post(
        "/organizations/",
        json={"name": "Test Organization"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"


def test_read_organizations(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/organizations/",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 200


def test_read_organization_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/organizations/999",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 404


def test_update_organization_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.put(
        "/organizations/999",
        json={"name": "Updated Organization"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_delete_organization_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.delete("/organizations/999",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_read_organization_appointments_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/organizations/999/appointments",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 404


def test_read_appointment_previous_versions_not_found(test_db, test_user):
    token = test_login_user(test_user)
    response = client.get("/appointments/999/previous_versions",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 404


def test_create_appointment_invalid(test_db, test_user):
    token = test_login_user(test_user)
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T09:00:00", "organization_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_create_user_invalid(test_db):
    response = client.post(
        "/users/signup",
        json={"username": "test", "password": "test1234", "email": ""},
    )

    assert response.status_code == 422


def test_create_user_invalid(test_db):
    response = client.post(
        "/users/signup",
        json={"username": "test", "password": "test1234", "email": ""},
    )

    assert response.status_code == 422
