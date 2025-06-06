from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
)

from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import datetime

DATABASE_URL = "postgresql://postgres:password@localhost/clinica"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ex: 1
    pseudonym = Column(String, nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    vitals = relationship("VitalSigns", back_populates="patient")
    labs = relationship("LabResult", back_populates="patient")
    scores = relationship("ClinicalScore", back_populates="patient")

class VitalSigns(Base):
    __tablename__ = "vital_signs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    heart_rate = Column(Integer)
    spo2 = Column(Float)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String)  # ex: "manual", "api"

    patient = relationship("Patient", back_populates="vitals")

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    test_name = Column(String)            # ex: CRP, leucocite
    value = Column(Float)
    units = Column(String)
    reference_range = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="labs")

class ClinicalScore(Base):
    __tablename__ = "clinical_scores"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    score_type = Column(String)           # ex: PEWS, NEWS
    score_value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="scores")

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # doctor, nurse, researcher

def init_db():
    Base.metadata.create_all(bind=engine)
    #Base.metadata.drop_all(bind=engine)  # Uncomment to drop all tables

if __name__ == "__main__":
    init_db()