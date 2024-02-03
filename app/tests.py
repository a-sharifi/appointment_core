import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .main import app
from .routers.appointments import check_appointment_valid
from .models import Appointment, Organization
from .schemas import AppointmentCreateSerializer, OrganizationCreateSerializer
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
    Base.metadata.drop_all(bind=engine)


# Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_appointment(test_db):
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
    )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["start"] == "2022-01-01T10:00:00"
    assert data["end"] == "2022-01-01T11:00:00"
    assert data["organization_id"] == 1


def test_create_appointment_conflict(test_db):
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
    )
    response = client.post(
        "/appointments/",
        json={"start": "2022-01-01T10:00:00", "end": "2022-01-01T11:00:00", "organization_id": 1},
    )
    assert response.status_code == 409


def test_read_appointments(test_db):
    response = client.get("/appointments/")
    assert response.status_code == 200


def test_read_appointment_not_found(test_db):
    response = client.get("/appointments/999")
    assert response.status_code == 404


def test_update_appointment_not_found(test_db):
    response = client.put(
        "/appointments/999",
        json={"start": "2022-01-01T12:00:00", "end": "2022-01-01T13:00:00", "organization_id": 1},
    )
    assert response.status_code == 404


def test_delete_appointment_not_found(test_db):
    response = client.delete("/appointments/999")
    assert response.status_code == 404


def test_create_organization(test_db):
    response = client.post(
        "/organizations/",
        json={"name": "Test Organization"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"


def test_read_organizations(test_db):
    response = client.get("/organizations/")
    assert response.status_code == 200


def test_read_organization_not_found(test_db):
    response = client.get("/organizations/999")
    assert response.status_code == 404


def test_update_organization_not_found(test_db):
    response = client.put(
        "/organizations/999",
        json={"name": "Updated Organization"},
    )
    assert response.status_code == 404


def test_delete_organization_not_found(test_db):
    response = client.delete("/organizations/999")
    assert response.status_code == 404


def test_read_organization_appointments_not_found(test_db):
    response = client.get("/organizations/999/appointments")
    assert response.status_code == 404


def test_read_appointment_previous_versions_not_found(test_db):
    response = client.get("/appointments/999/previous_versions")
    assert response.status_code == 404
