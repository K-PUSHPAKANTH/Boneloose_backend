from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime


# ---------------- USER ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    password = Column(String(255))
    role = Column(String(50))
    is_verified = Column(Boolean, default=True)

    analyses = relationship("Analysis", back_populates="owner")
    saved_cases = relationship("SavedCase", back_populates="owner")


# ---------------- ANALYSIS ----------------
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(String(50))
    image_path = Column(String(255))
    prediction = Column(String(50))
    confidence = Column(Float)
    bone_loss_percent = Column(Float, nullable=True)
    status = Column(String(50), default="Completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="analyses")


# ---------------- LEARNING MODULE ----------------
class LearningModule(Base):
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String(500))
    is_completed = Column(Boolean, default=False)


# ---------------- SAVED CASE ----------------
class SavedCase(Base):
    __tablename__ = "saved_cases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    bone_loss_percent = Column(Float)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="saved_cases")


# ---------------- SYSTEM METRICS ----------------
class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    total_users = Column(Integer)
    total_cases = Column(Integer)
    ai_accuracy = Column(Float)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------------- SYSTEM ALERT ----------------
class SystemAlert(Base):
    __tablename__ = "system_alerts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String(500))
    type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------------- USER ACTIVITY ----------------
class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True)
    active_users_24h = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())