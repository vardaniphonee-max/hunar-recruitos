from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(160))
    experience_min: Mapped[int] = mapped_column(Integer, default=0)
    experience_max: Mapped[int] = mapped_column(Integer, default=0)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)
    questions: Mapped[list["ScreeningQuestion"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class ScreeningQuestion(TimestampMixin, Base):
    __tablename__ = "screening_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    result_key: Mapped[str] = mapped_column(String(80))
    position: Mapped[int] = mapped_column(Integer)
    role: Mapped[Role] = relationship(back_populates="questions")
    __table_args__ = (UniqueConstraint("role_id", "result_key"),)


class Candidate(TimestampMixin, Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="manual", index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("source", "external_id"),)


class CandidateRole(TimestampMixin, Base):
    __tablename__ = "candidate_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(40), default="DISCOVERED", index=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    match_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    __table_args__ = (UniqueConstraint("role_id", "candidate_id"),)


class SearchRun(TimestampMixin, Base):
    __tablename__ = "search_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    provider: Mapped[str] = mapped_column(String(40))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    criteria: Mapped[dict[str, Any]] = mapped_column(JSON)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="DRAFT", index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Call(TimestampMixin, Base):
    __tablename__ = "calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    provider_call_id: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    request_id: Mapped[str] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(40), default="NOT_STARTED", index=True)
    lifecycle_status: Mapped[str] = mapped_column(String(40), default="NOT_STARTED")
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    raw_provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Transcript(TimestampMixin, Base):
    __tablename__ = "transcripts"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), unique=True)
    text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(40))


class StructuredAnswer(TimestampMixin, Base):
    __tablename__ = "structured_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[Any] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(40), default="provider")
    __table_args__ = (UniqueConstraint("call_id", "key"),)


class RecruiterReview(TimestampMixin, Base):
    __tablename__ = "recruiter_reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), unique=True)
    decision: Mapped[str] = mapped_column(String(60))
    note: Mapped[str] = mapped_column(Text)


class ActivityEvent(Base):
    __tablename__ = "activity_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(60), index=True)
    message: Mapped[str] = mapped_column(String(300))
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    call_id: Mapped[str] = mapped_column(String(80), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


Index("ix_activity_entity", ActivityEvent.entity_type, ActivityEvent.entity_id)
