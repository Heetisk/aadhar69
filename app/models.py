from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

class EnrolmentData(Base):
    __tablename__ = "enrolment_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    pincode = Column(String, index=True)
    age_0_5 = Column(Integer)
    age_5_17 = Column(Integer)
    age_17_plus = Column(Integer)

class DemographicUpdate(Base):
    __tablename__ = "demographic_update"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    pincode = Column(String, index=True)
    demo_age_5_17 = Column(Integer)
    demo_age_17_plus = Column(Integer)

class BiometricUpdate(Base):
    __tablename__ = "biometric_update"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    pincode = Column(String, index=True)
    bio_age_5_17 = Column(Integer)
    bio_age_17_plus = Column(Integer)
