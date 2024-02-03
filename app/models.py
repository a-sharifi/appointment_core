from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class AppointmentVersion(Base):
    __tablename__ = "appointment_versions"

    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    relationship("Appointment", backref="previous_versions")



class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    # Relationships
    organization = relationship("Organization", backref="appointments")
    previous_versions = relationship("AppointmentVersion", backref="appointment")
