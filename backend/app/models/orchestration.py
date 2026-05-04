from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
import uuid


DecisionType = Literal[
    "execute_now",
    "clarify",
    "defer",
    "reject",
    "schedule"
]

RiskLevel = Literal["low", "medium", "high"]

PriorityLevel = Literal["low", "medium", "high"]

ExecutionMode = Literal["sequential", "parallel", "hybrid"]

ReviewType = Literal["qa", "legal", "citation", "human"]

NodeStatus = Literal[
    "pending",
    "active",
    "blocked",
    "completed",
    "skipped"
]


@dataclass
class Interpretation:
    raw_prompt: str
    objective: str
    user_intent: str
    assumptions: List[str] = field(default_factory=list)
    clarifying_questions: List[str] = field(default_factory=list)


@dataclass
class Classification:
    task_type: str
    primary_department: str
    output_format: str
    project_context: str


@dataclass
class StrategicAssessment:
    strategic_fit: str
    urgency: str
    importance: str
    complexity: str
    estimated_effort_minutes: int
    reason: str


@dataclass
class ReviewPolicy:
    qa_required: bool = False
    legal_required: bool = False
    citation_required: bool = False
    human_review_required: bool = False
    reasons: List[str] = field(default_factory=list)


@dataclass
class HumanIntervention:
    required: bool
    reason: Optional[str] = None


@dataclass
class ContextPacket:
    id: str
    task_id: str
    original_prompt: str
    original_intent: str
    project_context: str
    founder_preferences: Dict[str, Any]
    constraints: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionStep:
    id: str
    department: str
    objective: str
    reason: str
    expected_input: str
    expected_output: str
    output_schema: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    can_run_parallel: bool = False
    estimated_time_minutes: int = 5
    model_choice: Optional[str] = None
    confidence_score: float = 0.75


@dataclass
class CEOEngineResult:
    task_id: str
    interpretation: Interpretation
    classification: Classification
    strategic_assessment: StrategicAssessment
    decision: DecisionType
    priority: PriorityLevel
    risk_level: RiskLevel
    execution_mode: ExecutionMode
    route: List[str]
    success_criteria: List[str]
    context_packet: ContextPacket
    delegation_plan: List[ExecutionStep]
    review_policy: ReviewPolicy
    human_intervention: HumanIntervention
    ceo_reasoning: str
    confidence_score: float


@dataclass
class DelegationNode:
    id: str
    task_id: str
    context_packet_id: str
    sender: str
    receiver: str
    message: str
    reason: str
    expected_input: str
    expected_output: str
    output_schema: Dict[str, Any]
    dependency_ids: List[str]
    status: NodeStatus = "pending"
    editable: bool = True
    estimated_time_minutes: int = 5
    model_choice: Optional[str] = None
    confidence_score: float = 0.75
    created_at: datetime = field(default_factory=datetime.utcnow)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

@dataclass
class PipelineContext:
    task: Any  # Use Any to avoid circular imports, but it's a Task
    original_prompt: str
    user_context: Dict[str, Any]
    ceo_result: Optional[CEOEngineResult] = None
    department_outputs: Dict[str, Any] = field(default_factory=dict)
    vidura_audits: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    status: str = "initialized"
    created_at: datetime = field(default_factory=datetime.utcnow)
