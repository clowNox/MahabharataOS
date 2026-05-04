from typing import Dict, Any, Optional
import uuid
from app.db.task_repo import get_campaign, save_campaign, save_task
from app.models.domain import Task
from app.engines.orchestrator import run_mahabharataos_task

def run_campaign_step(campaign_id: str, day: int, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single step (day) of a campaign.
    1. Loads campaign.
    2. Finds the step for the given day.
    3. Creates a new Task and persists it.
    4. Executes the task through the orchestrator.
    5. Updates the campaign plan with the task_id and status.
    """
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}
    
    plan = campaign.get("plan", [])
    step = next((s for s in plan if s.get("day") == day), None)
    
    if not step:
        return {"error": f"Day {day} not found in campaign {campaign_id}"}
    
    if step.get("status") == "completed":
        return {"message": f"Day {day} already completed", "task_id": step.get("task_id")}

    # Create a task for this campaign step
    task_id = str(uuid.uuid4())
    project_id = campaign.get("project_id") or "DC-P001"
    title = step.get("title", f"Campaign Day {day}")
    prompt = step.get("prompt")
    
    # Save the task to the DB
    save_task(
        task_id=task_id,
        project_id=project_id,
        title=title,
        prompt=prompt,
        context={} # api_keys are transient and handled by the orchestrator
    )
    
    # Execute the task
    task = Task(
        id=task_id,
        project_id=project_id,
        title=title,
        original_prompt=prompt,
        context={}
    )
    
    try:
        run_result = run_mahabharataos_task(task, user_context)
        
        # Update campaign plan step
        step["status"] = "completed"
        step["task_id"] = task_id
        step["last_run_id"] = run_result.get("run_id") # Note: run_mahabharataos_task currently doesn't return run_id, orchestrator.py:79-86 does the saving. 
        # Wait, run_mahabharataos_task in orchestrator.py returns a dict with outputs, ceo_result, etc. but it doesn't save the run.
        # Actually, looking at routes.py:134, execute_task calls run_mahabharataos_task AND THEN calls save_run.
        
        # I should probably move the save_run logic into a helper or call it here.
        
        from app.db.task_repo import save_run, save_delegation
        run_id = str(uuid.uuid4())
        
        chain_dicts = [node.__dict__ for node in run_result["delegation_chain"]]
        ceo_dict = run_result["ceo_result"].__dict__
        
        save_run(
            run_id=run_id,
            task_id=task_id,
            next_action=run_result["next_action"],
            ceo_result=ceo_dict,
            delegation_chain=chain_dicts,
            outputs=run_result["outputs"]
        )
        save_delegation(task_id=task_id, chain=chain_dicts)
        
        step["run_id"] = run_id
        save_campaign(campaign_id, campaign["title"], campaign["description"], plan)
        
        return {
            "status": "success",
            "day": day,
            "task_id": task_id,
            "run_id": run_id,
            "outputs": run_result["outputs"]
        }
    except Exception as e:
        step["status"] = "failed"
        step["error"] = str(e)
        save_campaign(campaign_id, campaign["title"], campaign["description"], plan)
        return {"error": f"Execution failed: {str(e)}"}

def run_next_campaign_step(campaign_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Finds the first non-completed step in the campaign and runs it.
    """
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}
    
    plan = campaign.get("plan", [])
    next_step = next((s for s in plan if s.get("status") != "completed"), None)
    
    if not next_step:
        return {"message": "All steps completed", "campaign_id": campaign_id}
    
    return run_campaign_step(campaign_id, next_step["day"], user_context)

