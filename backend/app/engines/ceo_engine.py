from typing import Dict, Any, List
from app.models.domain import Task

def interpret_task(prompt: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interprets the raw user prompt into a structured objective, capturing intent.
    """
    if "linkedin" in prompt.lower() or "post" in prompt.lower():
        return {
            "raw_prompt": prompt,
            "objective": f"Draft and publish a LinkedIn post",
            "user_intent": "Share thought leadership and startup building lessons",
            "assumptions": ["Audience is founders and builders", "Format should be raw and authentic"],
            "clarifying_questions": []
        }
        
    return {
        "raw_prompt": prompt,
        "objective": f"Execute general task: '{prompt[:50]}...'",
        "user_intent": "Complete requested action",
        "assumptions": [],
        "clarifying_questions": []
    }

def classify_task(interpretation: Dict[str, Any], project_context: str) -> Dict[str, str]:
    """Classifies the task."""
    obj_lower = interpretation["objective"].lower()
    if "linkedin" in obj_lower or "post" in obj_lower:
        return {
            "task_type": "thought_leadership",
            "primary_department": "media",
            "output_format": "text_post",
            "project_context": project_context
        }
    return {
        "task_type": "general_execution",
        "primary_department": "ceo_office",
        "output_format": "structured_response",
        "project_context": project_context
    }

def assess_strategy(interpretation: Dict[str, Any]) -> Dict[str, str]:
    """
    Evaluating whether the task aligns with current project priorities, user goals, 
    and available execution capacity.
    """
    # MVP Mock Logic
    return {
        "strategic_fit": "high",
        "urgency": "medium",
        "importance": "high",
        "complexity": "medium",
        "estimated_effort": "15 minutes"
    }

def make_decision(assessment: Dict[str, str]) -> str:
    """
    Decides whether to execute, defer, clarify, or reject.
    """
    if assessment["strategic_fit"] == "high" and assessment["importance"] == "high":
        return "execute_now"
    return "defer"

def assign_priority(assessment: Dict[str, str]) -> str:
    return "high" if assessment["urgency"] == "high" else "medium"

def assess_risk(interpretation: Dict[str, Any]) -> str:
    risky_keywords = ["guarantee", "fraud", "scam", "illegal", "promise"]
    prompt_lower = interpretation["raw_prompt"].lower()
    if any(keyword in prompt_lower for keyword in risky_keywords): return "high"
    if any(keyword in prompt_lower for keyword in ["market", "data", "report", "%"]): return "medium"
    return "low"

def generate_success_criteria(classification: Dict[str, str]) -> List[str]:
    if classification["task_type"] == "thought_leadership":
        return [
            "Generate 3 LinkedIn post options",
            "Preserve natural raw founder voice",
            "Complete within 15 minutes",
            "Flag factual or reputation risk"
        ]
    return ["Task executed successfully", "User intent preserved"]

def create_context_packet(task: Task, interpretation: Dict[str, Any]) -> Dict[str, Any]:
    """Context packet travels down the chain so intent isn't lost."""
    return {
        "original_intent": interpretation["user_intent"],
        "project_context": task.project_id,
        "founder_preferences": task.context.get("preferences", {})
    }

def select_execution_route(task_type: str, risk_level: str) -> List[str]:
    route = ["CEO Office"]
    if task_type in ["thought_leadership", "content_transformation"]:
        route.append("Media Department")
    if risk_level in ["high", "medium"]:
        route.append("QA & Compliance")
    route.append("Output Workspace")
    return route

def create_delegation_plan(route: List[str], priority: str) -> List[Dict[str, Any]]:
    steps = []
    for i, step in enumerate(route[1:]): 
        steps.append({
            "step_order": i + 1,
            "department": step,
            "objective": f"Execute standard procedure for {step}",
            "reason": f"Required as part of pipeline",
            "expected_output": f"Format required by {step}",
            "deadline": "15 minutes" if priority == "high" else "24 hours"
        })
    return steps

def decide_human_intervention(risk_level: str, priority: str, decision: str) -> Dict[str, Any]:
    if risk_level == "high":
        return {"required": True, "reason": "High risk content detected."}
    if decision == "clarify":
        return {"required": True, "reason": "CEO Engine needs clarification before proceeding."}
    return {"required": False, "reason": None}

def decide_review_policy(risk_level: str) -> Dict[str, Any]:
    return {
        "human_review_required": risk_level == "high",
        "qa_required": risk_level in ["medium", "high"],
        "legal_required": risk_level == "high",
        "citation_required": "if_factual" if risk_level == "medium" else risk_level == "high"
    }

def ceo_engine(task: Task, user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    The CEO Engine is the first intelligence layer after user input. 
    It converts raw objectives into strategic, editable execution plans.
    """
    interpretation = interpret_task(task.original_prompt, user_context)
    classification = classify_task(interpretation, task.project_id or "default")
    strategic_assessment = assess_strategy(interpretation)
    
    decision = make_decision(strategic_assessment)
    priority = assign_priority(strategic_assessment)
    risk_level = assess_risk(interpretation)
    
    route = select_execution_route(classification["task_type"], risk_level)
    delegation_plan = create_delegation_plan(route, priority)
    
    success_criteria = generate_success_criteria(classification)
    context_packet = create_context_packet(task, interpretation)
    
    review_policy = decide_review_policy(risk_level)
    human_intervention = decide_human_intervention(risk_level, priority, decision)
    
    return {
        "task_id": task.id,
        "interpretation": interpretation,
        "classification": classification,
        "strategic_assessment": strategic_assessment,
        "decision": decision,
        "priority": priority,
        "risk_level": risk_level,
        "route": route,
        "success_criteria": success_criteria,
        "context_packet": context_packet,
        "delegation_plan": delegation_plan,
        "review_policy": review_policy,
        "human_intervention": human_intervention
    }
