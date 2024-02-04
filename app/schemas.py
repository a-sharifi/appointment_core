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
    user_id: int
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
    user_id: int


class UserOutSerializer(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None

    class Config:
        orm_mode = True


class TokenSerializer(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        orm_mode = True


class TokenPayloadSerializer(BaseModel):
    sub: str = None
    exp: int
    username: str = None

    class Config:
        orm_mode = True


class UserAuthSerializer(BaseModel):
    username: str
    password: str
    email: str

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "username must be alphanumeric"
        return v

    @validator("password")
    def password_length(cls, v):
        assert len(v) >= 8, "password must be at least 8 characters"
        return v

    @validator("email")
    def email_valid(cls, v):
        assert "@" in v, "invalid email"
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123",
                "email": "test@test.com"
            }
        }


class UserLoginSerializer(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123"
            }
        }
