"""
routes.py
FastAPI router for tasks, execution, and delegation chain management.
Persistence: SQLite via task_repo (replaces MOCK_DB).
"""

import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.domain import Task
from app.engines.orchestrator import stream_mahabharataos_task
from app.engines.delegation_engine_v2 import update_delegation_chain
from app.db.task_repo import (
    save_task,
    get_task,
    get_all_tasks,
    get_tasks_count,
    update_task_status,
    save_run,
    get_latest_run,
    save_delegation,
    get_delegation,
    save_campaign,
    get_campaign,
)
from app.engines.campaign_runner import run_campaign_step, run_next_campaign_step
from app.services.vault import save_secret, get_all_secrets
from app.services.scheduler import schedule_campaign

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class TaskCreateRequest(BaseModel):
    project_id: Optional[str] = "DC-P001"
    title: str
    original_prompt: str
    context: Optional[Dict[str, Any]] = {}

class CampaignRequest(BaseModel):
    theme: str
    duration_days: int = 7

class VaultSecretRequest(BaseModel):
    key: str
    value: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_task_or_404(task_id: str) -> dict:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/tasks", response_model=Task, summary="Create a new task")
def create_task(
    request: TaskCreateRequest,
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
    x_tavily_key: str = Header(None),
    x_gemini_key: str = Header(None),
):
    """
    Creates and persists a new task from a raw user objective.
    API keys passed via headers are injected into the task context
    for use by downstream LLM agents — they are NOT stored to disk.
    """
    task_id = str(uuid.uuid4())

    # Build transient context — keys live only in this request's memory,
    # they are intentionally excluded from DB persistence (context col).
    persisted_context = dict(request.context or {})
    persisted_context.pop("api_keys", None)   # never persist keys

    save_task(
        task_id=task_id,
        project_id=request.project_id or "DC-P001",
        title=request.title,
        prompt=request.original_prompt,
        context=persisted_context,
    )

    return Task(
        id=task_id,
        project_id=request.project_id,
        title=request.title,
        original_prompt=request.original_prompt,
        context=persisted_context,
    )


@router.post("/tasks/{task_id}/execute", summary="Execute a task through the full OS pipeline")
def execute_task(
    task_id: str,
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
    x_tavily_key: str = Header(None),
    x_gemini_key: str = Header(None),
):
    """
    Runs the full mahabharataOS orchestrator: CEO → Risk → Delegation → Media.
    API keys are injected into a transient user_context dict and never persisted.
    """
    stored = _load_task_or_404(task_id)

    # Build transient user_context — keys only live for this request
    user_context = dict(stored.get("context") or {})
    user_context.setdefault("api_keys", {})
    if x_openai_key:
        user_context["api_keys"]["openai"] = x_openai_key
    if x_anthropic_key:
        user_context["api_keys"]["anthropic"] = x_anthropic_key
    if x_tavily_key:
        user_context["api_keys"]["tavily"] = x_tavily_key
    if x_gemini_key:
        user_context["api_keys"]["gemini"] = x_gemini_key

    task = Task(
        id=stored["id"],
        project_id=stored.get("project_id"),
        title=stored["title"],
        original_prompt=stored["original_prompt"],
        context={},   # don't pass keys into Task model
    )

    # Stream the orchestration steps via Server‑Sent Events
    return StreamingResponse(
        stream_mahabharataos_task(task, user_context=user_context),
        media_type="text/event-stream",
    )


@router.post("/campaigns/generate", summary="Generate a weekly content batch plan")
def generate_campaign_plan_endpoint(
    request: CampaignRequest,
    x_openai_key: str = Header(None),
):
    """
    Takes a theme and generates a daily plan of tasks.
    Persists the generated campaign to the database.
    """
    from app.engines.campaign_engine import generate_campaign_plan
    
    user_context = {"api_keys": {"openai": x_openai_key}}
    
    plan = generate_campaign_plan(
        theme=request.theme,
        duration_days=request.duration_days,
        user_context=user_context
    )

    campaign_id = str(uuid.uuid4())
    save_campaign(
        campaign_id=campaign_id,
        title=f"Campaign: {request.theme}",
        description=f"{request.duration_days}-day strategic content batch",
        plan=plan
    )
    
    return {
        "status": "success",
        "campaign_id": campaign_id,
        "theme": request.theme,
        "duration_days": request.duration_days,
        "plan": plan
    }


@router.get("/tasks", summary="List all tasks")
def list_tasks_endpoint(
    skip: int = 0,
    limit: int = 50,
):
    """Returns all tasks ordered by newest first, with derived status from run state."""
    return get_all_tasks(skip=skip, limit=limit)


@router.get("/tasks/count", summary="Total task count")
def task_count_endpoint():
    return {"count": get_tasks_count()}


@router.get("/tasks/{task_id}", response_model=Task, summary="Get a task by ID")
def get_task_endpoint(task_id: str):
    stored = _load_task_or_404(task_id)
    return Task(**{k: stored[k] for k in ("id", "project_id", "title", "original_prompt", "context")})


class TaskStatusUpdate(BaseModel):
    status: str


@router.patch("/tasks/{task_id}/status", summary="Update task status")
def update_task_status_endpoint(task_id: str, body: TaskStatusUpdate):
    """
    Updates the status of a task. Valid values: pending, approved, rejected.
    Called by the frontend Approve & Deploy button.
    """
    _load_task_or_404(task_id)
    allowed = {"pending", "approved", "rejected", "in_progress", "pending_review"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status '{body.status}'. Allowed: {allowed}")
    updated = update_task_status(task_id=task_id, status=body.status)
    if not updated:
        raise HTTPException(status_code=500, detail="Status update failed")
    return {"status": "ok", "task_id": task_id, "new_status": body.status}


@router.get("/tasks/{task_id}/delegation", summary="Get delegation chain for a task")
def get_delegation_chain_endpoint(task_id: str):
    """Retrieves the persisted delegation chain for a task."""
    _load_task_or_404(task_id)   # 404 if task doesn't exist
    chain = get_delegation(task_id)
    if chain is None:
        raise HTTPException(status_code=404, detail="No delegation chain found — task not yet executed")
    return chain


@router.patch("/tasks/{task_id}/delegation", summary="Update delegation chain for a task")
def update_delegation_chain_endpoint(task_id: str, updated_nodes: List[Dict[str, Any]]):
    """Allows the frontend to save an edited delegation chain."""
    _load_task_or_404(task_id)

    current_chain_dicts = get_delegation(task_id) or []
    # update_delegation_chain expects DelegationNode objects — rebuild them
    from app.models.orchestration import DelegationNode
    current_objects = [DelegationNode(**n) for n in current_chain_dicts]
    new_chain = update_delegation_chain(current_objects, updated_nodes)
    new_dicts = [node.__dict__ for node in new_chain]
    save_delegation(task_id=task_id, chain=new_dicts)

    return {
        "status": "updated",
        "task_id": task_id,
        "new_chain": new_dicts,
    }


@router.get("/campaigns/{campaign_id}", summary="Get a campaign by ID")
def get_campaign_endpoint(campaign_id: str):
    campaign = get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")
    return campaign


@router.get("/tasks/{task_id}/latest_run", summary="Get the most recent run for a task")
def get_latest_run_endpoint(task_id: str):
    """Retrieves the last execution outputs and delegation chain."""
    _load_task_or_404(task_id)
    run = get_latest_run(task_id)
    if not run:
        raise HTTPException(status_code=404, detail="No run found for this task")
    return run


@router.post("/campaigns/{campaign_id}/execute/{day}", summary="Execute a specific day of a campaign")
def execute_campaign_day_endpoint(
    campaign_id: str,
    day: int,
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
    x_tavily_key: str = Header(None),
    x_gemini_key: str = Header(None),
):
    """
    Executes a single day's task from a campaign.
    """
    user_context = {"api_keys": {}}
    if x_openai_key: user_context["api_keys"]["openai"] = x_openai_key
    if x_anthropic_key: user_context["api_keys"]["anthropic"] = x_anthropic_key
    if x_tavily_key: user_context["api_keys"]["tavily"] = x_tavily_key
    if x_gemini_key: user_context["api_keys"]["gemini"] = x_gemini_key
    
    result = run_campaign_step(campaign_id, day, user_context)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/campaigns/{campaign_id}/execute_next", summary="Execute the next pending day of a campaign")
def execute_next_campaign_day_endpoint(
    campaign_id: str,
    x_openai_key: str = Header(None),
    x_anthropic_key: str = Header(None),
    x_tavily_key: str = Header(None),
    x_gemini_key: str = Header(None),
):
    """
    Finds and executes the next pending day's task from a campaign.
    """
    user_context = {"api_keys": {}}
    if x_openai_key: user_context["api_keys"]["openai"] = x_openai_key
    if x_anthropic_key: user_context["api_keys"]["anthropic"] = x_anthropic_key
    if x_tavily_key: user_context["api_keys"]["tavily"] = x_tavily_key
    if x_gemini_key: user_context["api_keys"]["gemini"] = x_gemini_key
    
    result = run_next_campaign_step(campaign_id, user_context)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/campaigns/{campaign_id}/schedule", summary="Schedule a campaign for autonomous execution")
def schedule_campaign_endpoint(campaign_id: str):
    """
    Schedules a campaign to run one step per day starting shortly.
    """
    schedule_campaign(campaign_id)
    return {"status": "scheduled", "campaign_id": campaign_id}


@router.post("/vault/save", summary="Save a secret to the secure vault")
def save_vault_secret(request: VaultSecretRequest):
    """
    Encrypts and persists a secret (e.g. API key) to the server-side vault.
    """
    save_secret(request.key, request.value)
    return {"status": "saved", "key": request.key}


@router.get("/vault/status", summary="Check which keys are in the vault")
def get_vault_status():
    """Returns a list of keys currently stored in the vault (values masked)."""
    secrets = get_all_secrets()
    return {"keys": list(secrets.keys())}


@router.get("/chronicle/list", summary="List all memory entries")
def list_chronicle_entries(limit: int = 20):
    from app.services.memory import chronicle
    return chronicle.metadata[-limit:][::-1] # Newest first


@router.get("/chronicle/search", summary="Search semantic memory")
async def search_chronicle(query: str, x_openai_key: str = Header(None)):
    from app.services.memory import chronicle
    import numpy as np
    import openai
    
    if not x_openai_key:
        raise HTTPException(status_code=400, detail="OpenAI key required for semantic search")
        
    try:
        client = openai.AsyncOpenAI(api_key=x_openai_key)
        resp = await client.embeddings.create(
            input=[query.replace("\n", " ")],
            model="text-embedding-3-small"
        )
        query_emb = np.array(resp.data[0].embedding)
        return chronicle.search(query_emb, limit=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
