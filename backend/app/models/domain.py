from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str
    name: str
    role: str = "Director"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    active_project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Project(BaseModel):
    id: str
    code: str
    name: str
    status: str
    project_type: str
    primary_owner: str
    supporting_departments: List[str] = Field(default_factory=list)
    goal: str
    review_frequency: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    id: str
    project_id: Optional[str] = None
    title: str
    original_prompt: str
    created_by: str = "System"
    assigned_to: Optional[str] = None
    priority: str = "medium"
    risk_level: str = "low"
    status: str = "pending"
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DelegationNode(BaseModel):
    id: str
    task_id: str
    sender: str
    receiver: str
    message: str
    reason: str
    expected_output: str
    status: str = "pending"
    editable: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Output(BaseModel):
    id: str
    task_id: str
    agent_id: str
    output_type: str
    content: str
    version: int = 1
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
