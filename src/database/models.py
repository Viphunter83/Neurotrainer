"""
SQLAlchemy ORM models for database tables.

Complete schema with all models: User, ExerciseSession, FrameAnalysis,
Achievement, WorkoutPlan, DailyStats.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.database import Base


# ============ USER MANAGEMENT ============


class User(Base):
    """
    User model for authentication and user management.

    Stores user profile, preferences, and aggregated metrics.
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Personal Info
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)

    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)

    # Profile
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # "M", "F", "Other"
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Preferences
    language = Column(String(5), default="en")  # "en", "ru", etc
    timezone = Column(String(50), default="UTC")
    difficulty_level = Column(
        String(20), default="beginner"
    )  # "beginner", "intermediate", "advanced"

    # Role and Security
    role = Column(String(20), default="user")  # "admin", "trainer", "user", "guest"
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Settings
    tts_enabled = Column(Boolean, default=True)
    feedback_enabled = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)

    # Metrics
    total_workouts = Column(Integer, default=0)
    total_reps = Column(Integer, default=0)
    avg_form_score = Column(Float, nullable=True)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions = relationship(
        "ExerciseSession", back_populates="user", cascade="all, delete-orphan"
    )
    achievements = relationship(
        "Achievement", back_populates="user", cascade="all, delete-orphan"
    )
    workout_plans = relationship(
        "WorkoutPlan", back_populates="user", cascade="all, delete-orphan"
    )
    daily_stats = relationship(
        "DailyStats", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


# ============ EXERCISE SESSIONS ============


class ExerciseSession(Base):
    """
    Exercise session model for tracking workout sessions.

    Each time a user starts an exercise, a record is created.
    """

    __tablename__ = "exercise_sessions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Session Info
    exercise_type = Column(
        String(50), nullable=False, index=True
    )  # "squat", "pushup", etc
    status = Column(
        String(20), default="active"
    )  # "active", "paused", "completed", "cancelled"

    # Duration
    started_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Metrics
    total_reps = Column(Integer, default=0)
    avg_form_score = Column(Float, nullable=True)
    max_form_score = Column(Float, nullable=True)
    min_form_score = Column(Float, nullable=True)

    # Analysis Summary
    common_errors = Column(ARRAY(String), nullable=True)  # ["back_hunched", "knees_forward"]

    # Settings for this session
    settings = Column(JSON, nullable=True)  # {"feedback_enabled": true, "tts_enabled": false}

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    frame_analyses = relationship(
        "FrameAnalysis",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="FrameAnalysis.frame_id",
    )

    # Indexes
    __table_args__ = (
        Index("idx_session_user_type", "user_id", "exercise_type"),
        Index("idx_session_started_at", "started_at"),
        Index("idx_session_user_started", "user_id", "started_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ExerciseSession(id={self.id}, user_id={self.user_id}, "
            f"exercise_type={self.exercise_type}, status={self.status}, "
            f"total_reps={self.total_reps})>"
        )


# ============ FRAME ANALYSIS ============


class FrameAnalysis(Base):
    """
    Frame analysis model for individual frame analysis.

    Time-series data: one analysis per frame (~30 frames per second).

    Optimized for TimescaleDB hypertable.
    """

    __tablename__ = "frame_analyses"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exercise_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Frame Info
    frame_id = Column(Integer, nullable=False)  # Sequential frame number in session
    timestamp = Column(
        DateTime(timezone=True), default=func.now(), index=True
    )  # TimescaleDB time index

    # Analysis Results
    phase = Column(String(50), nullable=False)  # "standing", "descending", "bottom", "ascending"
    rep_count = Column(Integer, nullable=False)  # Cumulative rep count at this frame

    # Angles (in degrees)
    knee_angle = Column(Float, nullable=False)
    hip_angle = Column(Float, nullable=True)
    back_angle = Column(Float, nullable=True)

    # Quality Score
    form_score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # Model confidence 0-1

    # Errors detected
    errors = Column(ARRAY(String), nullable=True)  # ["back_hunched", "insufficient_depth"]

    # Keypoints (for visualization, JSON)
    keypoints = Column(JSON, nullable=True)  # [{x, y, z, visibility}, ...]

    # Performance metrics
    inference_time_ms = Column(Float, nullable=True)
    processing_time_ms = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    session = relationship("ExerciseSession", back_populates="frame_analyses")

    # Indexes for time-series queries
    __table_args__ = (
        Index("idx_frame_session_time", "session_id", "timestamp"),
        Index("idx_frame_rep_count", "session_id", "rep_count"),
        Index("idx_frame_session_frame", "session_id", "frame_id"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<FrameAnalysis(id={self.id}, session_id={self.session_id}, "
            f"frame_id={self.frame_id}, phase={self.phase}, rep_count={self.rep_count})>"
        )


# ============ ACHIEVEMENTS & GAMIFICATION ============


class Achievement(Base):
    """
    Achievement model for user achievements.

    Tracks user accomplishments and milestones.
    """

    __tablename__ = "achievements"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Achievement Info
    achievement_type = Column(
        String(100), nullable=False, index=True
    )
    # Examples: "first_100_squats", "7_day_streak", "perfect_form", "speed_record"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)

    # Metadata
    achievement_metadata = Column(JSON, nullable=True)  # {"reps": 100, "date": "2025-11-09"}

    # Timestamps
    earned_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship("User", back_populates="achievements")

    # Indexes
    __table_args__ = (
        Index("idx_achievement_user_type", "user_id", "achievement_type"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Achievement(id={self.id}, user_id={self.user_id}, "
            f"achievement_type={self.achievement_type}, title={self.title})>"
        )


# ============ WORKOUT PLANS ============


class WorkoutPlan(Base):
    """
    Workout plan model for personalized training plans.

    For future feature: personalized workout plans.
    """

    __tablename__ = "workout_plans"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Plan Info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(
        String(20), nullable=False
    )  # "beginner", "intermediate", "advanced"

    # Duration
    duration_days = Column(Integer, nullable=False)  # e.g., 30, 60, 90
    exercises_per_week = Column(Integer, default=3)

    # Plan structure
    plan_data = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "weeks": [
    #     {
    #       "week": 1,
    #       "focus": "form",
    #       "days": [
    #         {"day": 1, "exercise": "squat", "sets": 3, "reps": 10, "rest_seconds": 60}
    #       ]
    #     }
    #   ]
    # }

    # Status
    is_active = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # For template plans

    # Tracking
    total_completed_sessions = Column(Integer, default=0)
    completion_percent = Column(Float, default=0.0)

    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="workout_plans")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<WorkoutPlan(id={self.id}, user_id={self.user_id}, "
            f"name={self.name}, difficulty_level={self.difficulty_level})>"
        )


# ============ STATISTICS & ANALYTICS ============


class DailyStats(Base):
    """
    Aggregated daily statistics.

    For fast retrieval of charts and analytics.
    """

    __tablename__ = "daily_stats"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Date
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Daily Metrics
    total_workouts = Column(Integer, default=0)
    total_reps = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    avg_form_score = Column(Float, nullable=True)

    # Exercise breakdown
    exercises_breakdown = Column(JSON, nullable=True)
    # {"squat": {"reps": 50, "avg_score": 85}, "pushup": {"reps": 30, "avg_score": 80}}

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="daily_stats")

    # Indexes
    __table_args__ = (
        Index("idx_daily_stats_user_date", "user_id", "date"),
        Index("idx_daily_stats_date", "date"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<DailyStats(id={self.id}, user_id={self.user_id}, "
            f"date={self.date}, total_reps={self.total_reps})>"
        )


# ============ TOKEN BLACKLIST ============


class TokenBlacklist(Base):
    """
    Token blacklist model for revoked tokens.

    Used for logout and token revocation.
    """

    __tablename__ = "token_blacklist"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Token info
    jti = Column(String(500), unique=True, index=True, nullable=False)
    # JTI (JWT ID) - уникальный идентификатор токена

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    token_type = Column(String(20))  # "access" или "refresh"

    # Timestamps
    blacklisted_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Reason
    reason = Column(String(255))  # "logout", "password_changed", "security_alert"

    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_blacklist_user_expires", "user_id", "expires_at"),
        Index("idx_blacklist_jti", "jti"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<TokenBlacklist(id={self.id}, user_id={self.user_id}, "
            f"jti={self.jti}, token_type={self.token_type})>"
        )


# ============ PUSH TOKENS ============


class PushToken(Base):
    """
    Push token model for FCM (Firebase Cloud Messaging) tokens.
    
    Stores device push notification tokens for sending notifications.
    """

    __tablename__ = "push_tokens"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token Info
    token = Column(String(500), nullable=False, unique=True, index=True)
    platform = Column(String(20), nullable=False)  # "ios" or "android"
    device_id = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="push_tokens")

    # Indexes
    __table_args__ = (
        Index("idx_push_token_user_active", "user_id", "is_active"),
        Index("idx_push_token_platform", "platform"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<PushToken(id={self.id}, user_id={self.user_id}, "
            f"platform={self.platform}, is_active={self.is_active})>"
        )
