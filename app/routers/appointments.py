import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette import status

from ..dependencies import get_current_db, get_current_user
from ..models import Appointment, AppointmentVersion, User
from ..schemas import AppointmentCreateSerializer, AppointmentSerializer

router = APIRouter(
    prefix="/appointments",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


def check_appointment_valid(appointment: AppointmentCreateSerializer, db: Session):
    existing_appointment = db.query(Appointment).filter(
        (
                (Appointment.start == appointment.start) & (Appointment.end == appointment.end) & (
                Appointment.organization_id == appointment.organization_id)
        ) |
        (
                (Appointment.start < appointment.start) & (Appointment.end > appointment.start) & (
                Appointment.organization_id == appointment.organization_id)
        )
    ).first()
    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment already exists")


@router.post("/", response_model=AppointmentSerializer)
async def create_appointment(appointment: AppointmentCreateSerializer, db: Session = Depends(get_current_db),
                             user=Depends(get_current_user)):
    check_appointment_valid(appointment, db)

    # Validate appointment data
    appointment_model = Appointment(**appointment.model_dump(), created_at=datetime.datetime.now(),
                                    updated_at=datetime.datetime.now(), user_id=user.id)
    db.add(appointment_model)
    db.commit()
    db.refresh(appointment_model)  # Reload latest data from database
    return appointment_model


@router.get("/", response_model=list[AppointmentSerializer])
async def read_appointments(skip: int = 0, limit: int = 10, db: Session = Depends(get_current_db),
                            user=Depends(get_current_user)):
    appointments = db.query(Appointment).filter(Appointment.user_id == user.id).offset(skip).limit(limit).all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentSerializer)
async def read_appointment(appointment_id: int, db: Session = Depends(get_current_db),
                           user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(
        (Appointment.id == appointment_id) & (Appointment.user_id == user.id)).first()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentSerializer)
async def update_appointment(appointment_id: int, appointment: AppointmentCreateSerializer,
                             db: Session = Depends(get_current_db), user: User = Depends(get_current_user)):
    # Check if appointment exists
    existing_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id & Appointment.user_id == user.id).first()
    check_appointment_valid(appointment, db)
    if existing_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    appointment_version = AppointmentVersion(appointment_id=appointment_id, start=existing_appointment.start,
                                             end=existing_appointment.end, created_at=datetime.datetime.now())
    # Update appointment data
    appointment_model = Appointment(**appointment.model_dump(), updated_at=datetime.datetime.now())
    db.add(appointment_model)
    db.add(appointment_version)
    db.commit()
    db.refresh(appointment_model)
    return appointment_model


@router.delete("/{appointment_id}", response_model=AppointmentSerializer)
async def delete_appointment(appointment_id: int, db: Session = Depends(get_current_db)):
    # Check if appointment exists
    existing_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if existing_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # Delete appointment
    db.delete(existing_appointment)
    db.commit()
    return existing_appointment


@router.get("/{appointment_id}/previous_versions")
async def read_appointment_previous_versions(appointment_id: int, db: Session = Depends(get_current_db),
                                             user: User = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.user_id == user.id).first()

    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment.previous_versions
