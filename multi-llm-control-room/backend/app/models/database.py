"""SQLAlchemy database models"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    tags = Column(ARRAY(String), default=list)


class SessionModel(Base):
    """Session model"""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    routing_pattern = Column(String(50), nullable=False)
    models = Column(JSON, nullable=False)  # Array of ModelConfig
    coordinator_model_id = Column(String(100), nullable=True)
    framework_config = Column(JSON, nullable=True)
    mcp_servers = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(50), nullable=False, default="active")
    cost_limit = Column(Float, nullable=True)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)


class MessageModel(Base):
    """Message model"""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    model_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    metadata = Column(JSON, default=dict)


class CostTracking(Base):
    """Cost tracking model"""
    __tablename__ = "cost_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"))
    model_id = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class Run(Base):
    """Experiment/YouTube run model"""
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="running")
    config_snapshot = Column(JSON, nullable=False)
    inputs = Column(JSON, nullable=True)
    outputs = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), default=list)
    youtube_metadata = Column(JSON, nullable=True)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=0)
