from pydantic import BaseModel, validator
from typing import List
import datetime


class AppointmentCreateSerializer(BaseModel):
    start: datetime.datetime
    end: datetime.datetime
    organization_id: int

    @validator("end")
    def end_after_start(cls, v, values):
        if v <= values.get("start"):
            raise ValueError("End time must be after start time")
        return v


class AppointmentUpdateSerializer(BaseModel):
    start: datetime.datetime
    end: datetime.datetime
    organization_id: int

    @validator("start")
    def start_not_null(cls, v):
        if v is None:
            raise ValueError("Start time is required for updates")

    @validator("end")
    def end_after_start(cls, v, values):
        print(v, values)
        if v is not None and v <= values.get("start"):
            raise ValueError("End time must be after start time")


class AppointmentSerializer(BaseModel):
    id: int
    organization_id: int
    start: datetime.datetime
    end: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class OrganizationCreateSerializer(BaseModel):
    name: str


class OrganizationUpdateSerializer(BaseModel):
    name: str


class OrganizationSerializer(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
