from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    linkedin_url = Column(Text)
    phone = Column(Text)
    years_experience = Column(Integer)
    skills = Column(ARRAY(Text), default=[])
    job_titles = Column(ARRAY(Text), default=[])
    education = Column(JSONB, default=[])
    writing_style = Column(Text)
    embedding = Column(Text)  # Store as text to avoid pgvector dependency issues
    cv_file_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    company = Column(Text, nullable=False)
    company_logo = Column(Text)
    location = Column(Text)
    is_remote = Column(Boolean, default=True)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(Text, default="USD")
    description = Column(Text, nullable=False)
    requirements = Column(ARRAY(Text), default=[])
    tags = Column(ARRAY(Text), default=[])
    source = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    apply_url = Column(Text, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=False)
    embedding = Column(Text)  # Store as text to avoid pgvector dependency issues
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, nullable=False, default="draft")
    cover_letter = Column(Text)
    form_data = Column(JSONB, default={})
    submitted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
