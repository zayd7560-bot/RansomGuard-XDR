from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean
)

from datetime import datetime

from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


# ===========================
# Users Table
# ===========================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    duress_password_hash = Column(String, nullable=False)

    role = Column(String, default="User")

    created_at = Column(DateTime, default=datetime.utcnow)

    profile_image = Column(String, nullable=True)


# ===========================
# Devices Table
# ===========================

class Device(Base):

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    device_uuid = Column(String, unique=True)

    device_name = Column(String)

    os = Column(String)

    version = Column(String)

    status = Column(String, default="Offline")

    protection = Column(Boolean, default=True)

    realtime = Column(Boolean, default=True)

    files_scanned = Column(Integer, default=0)

    threats_blocked = Column(Integer, default=0)

    last_login = Column(DateTime)

    last_scan = Column(DateTime)

    threat_level = Column(String, default="NORMAL")

# ===========================
# Incidents Table
# ===========================

class Incident(Base):

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)

    username = Column(String)

    device_uuid = Column(String)

    threat_score = Column(Float)

    entropy = Column(Float)

    modified_files = Column(Integer)

    action = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )