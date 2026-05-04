from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    original_prompt = Column(String, nullable=False)
    status = Column(String, default="pending")
    priority = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    # Relationships
    nodes = relationship("DelegationNodeModel", back_populates="task")
    output = relationship("OutputModel", back_populates="task", uselist=False)

class DelegationNodeModel(Base):
    __tablename__ = "delegation_nodes"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"))
    department = Column(String, nullable=False)
    objective = Column(String, nullable=False)
    status = Column(String, default="pending")
    model_choice = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    task = relationship("TaskModel", back_populates="nodes")

class OutputModel(Base):
    __tablename__ = "outputs"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id"))
    format = Column(String, nullable=False)
    content = Column(JSON, nullable=False) # Store the drafts or final post
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)
    
    task = relationship("TaskModel", back_populates="output")

class MemoryItemModel(Base):
    __tablename__ = "memory_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    priority = Column(String, nullable=False) # P1 (Permanent), P2 (Review), P3 (Expiry)
    content = Column(String, nullable=False)
    source_department = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
