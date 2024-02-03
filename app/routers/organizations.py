import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_current_db
from ..models import Organization
from ..schemas import OrganizationSerializer, OrganizationCreateSerializer, OrganizationUpdateSerializer

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    responses={404: {"description": "Not found"}},

)


@router.post("/", response_model=OrganizationSerializer)
async def create_organization(organization: OrganizationCreateSerializer, db: Session = Depends(get_current_db)):
    organization_model = Organization(**organization.model_dump(), created_at=datetime.datetime.now(),
                                      updated_at=datetime.datetime.now())
    db.add(organization_model)
    db.commit()
    db.refresh(organization_model)
    return organization_model


@router.get("/", response_model=list[OrganizationSerializer])
async def read_organizations(skip: int = 0, limit: int = 10, db: Session = Depends(get_current_db)):
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations


@router.get("/{organization_id}")
async def read_organization(organization_id: int, db: Session = Depends(get_current_db)):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.put("/{organization_id}", response_model=OrganizationSerializer)
async def update_organization(organization_id: int, organization: OrganizationUpdateSerializer,
                              db: Session = Depends(get_current_db)):
    # Check if organization exists
    existing_organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if existing_organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Update organization data
    organization_model = Organization(**organization.model_dump())
    db.add(organization_model)
    db.commit()
    db.refresh(organization_model)
    return organization_model


@router.delete("/{organization_id}", response_model=OrganizationSerializer)
async def delete_organization(organization_id: int, db: Session = Depends(get_current_db)):
    # Check if organization exists
    existing_organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if existing_organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Delete organization
    db.delete(existing_organization)
    db.commit()
    return existing_organization


@router.get("/{organization_id}/appointments")
async def read_organization_appointments(organization_id: int, db: Session = Depends(get_current_db)):
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization.appointments
