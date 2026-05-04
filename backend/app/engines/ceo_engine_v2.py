from typing import Dict, Any, List
from app.models.domain import Task
from app.models.orchestration import (
    Interpretation,
    Classification,
    StrategicAssessment,
    ContextPacket,
    ExecutionStep,
    CEOEngineResult,
    new_id,
)
from app.engines.risk_engine import (
    assess_risk_from_text,
    decide_review_policy,
    decide_human_intervention,
)
from app.engines.model_router import choose_model_for_step, call_openai
from app.services.memory import chronicle
import json
import numpy as np


def interpret_task(prompt: str, user_context: Dict[str, Any]) -> Interpretation:
    system_prompt = """You are the CEO Intelligence Engine. 
Extract the user's intent from the following prompt. 
Return ONLY valid JSON matching this exact schema:
{
  "objective": "str",
  "user_intent": "str",
  "assumptions": ["str", "str"]
}
Do not include markdown code blocks. Just return the raw JSON."""

    try:
        api_keys = user_context.get("api_keys", {})
        openai_key = api_keys.get("openai", None)
        
        response = call_openai(prompt, system_prompt, api_key=openai_key)
        if "MOCK:" in response:
            raise ValueError("No API Key")
            
        clean_json = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        return Interpretation(
            raw_prompt=prompt,
            objective=data.get("objective", "Execute the objective"),
            user_intent=data.get("user_intent", "Complete the task"),
            assumptions=data.get("assumptions", []),
            clarifying_questions=[]
        )
    except Exception as e:
        # Fallback to deterministic logic if LLM fails or no key is present
        lower = prompt.lower()
        if "linkedin" in lower or "post" in lower:
            return Interpretation(
                raw_prompt=prompt,
                objective="Create a LinkedIn thought leadership post.",
                user_intent="Document founder journey and build public authority.",
                assumptions=["Audience includes founders, builders, operators.", "Maintain raw voice."],
                clarifying_questions=[]
            )
        return Interpretation(
            raw_prompt=prompt,
            objective="Execute the requested objective (Fallback).",
            user_intent="Complete the task with clarity.",
            assumptions=["Task should be completed simply."],
            clarifying_questions=[]
        )


def classify_task(
    interpretation: Interpretation,
    project_context: str
) -> Classification:
    prompt = interpretation.raw_prompt.lower()

    if any(keyword in prompt for keyword in ["linkedin", "post", "write", "draft", "story", "narrative"]):
        return Classification(
            task_type="thought_leadership",
            primary_department="Media Department",
            output_format="linkedin_post",
            project_context=project_context
        )

    if "carousel" in prompt:
        return Classification(
            task_type="content_transformation",
            primary_department="Media Department",
            output_format="carousel",
            project_context=project_context
        )

    if "research" in prompt or "latest" in prompt:
        return Classification(
            task_type="research",
            primary_department="Research Department",
            output_format="research_brief",
            project_context=project_context
        )

    if "cost" in prompt or "budget" in prompt or "runway" in prompt:
        return Classification(
            task_type="finance",
            primary_department="Finance & Capital Office",
            output_format="financial_note",
            project_context=project_context
        )

    return Classification(
        task_type="general_execution",
        primary_department="CEO Office",
        output_format="structured_output",
        project_context=project_context
    )


def assess_strategy(
    interpretation: Interpretation,
    classification: Classification,
    user_context: Dict[str, Any]
) -> StrategicAssessment:
    active_project = user_context.get("active_project", "DC-P001")
    daily_time_limit = user_context.get("daily_time_limit_minutes", 30)

    if classification.project_context == active_project:
        strategic_fit = "high"
    else:
        strategic_fit = "medium"

    if classification.task_type == "thought_leadership":
        importance = "high"
        urgency = "high"
        estimated_effort = 15
        reason = "Thought Leadership is the active Project 1 and requires daily execution."
    elif classification.task_type == "research":
        importance = "medium"
        urgency = "medium"
        estimated_effort = 20
        reason = "Research may support better decisions but should not block daily execution unless essential."
    elif classification.task_type == "finance":
        importance = "high"
        urgency = "medium"
        estimated_effort = 25
        reason = "Financial clarity is important, but timing depends on decision urgency."
    else:
        importance = "medium"
        urgency = "medium"
        estimated_effort = 20
        reason = "General task has useful value but requires prioritization."

    complexity = "high" if estimated_effort > daily_time_limit else "medium"

    return StrategicAssessment(
        strategic_fit=strategic_fit,
        urgency=urgency,
        importance=importance,
        complexity=complexity,
        estimated_effort_minutes=estimated_effort,
        reason=reason
    )


def make_decision(
    assessment: StrategicAssessment,
    interpretation: Interpretation
) -> str:
    if interpretation.clarifying_questions:
        return "clarify"

    if assessment.strategic_fit == "high" and assessment.importance == "high":
        return "execute_now"

    if assessment.urgency == "low" and assessment.importance == "low":
        return "reject"

    if assessment.strategic_fit == "medium":
        return "schedule"

    return "defer"


def assign_priority(assessment: StrategicAssessment) -> str:
    if assessment.importance == "high" and assessment.urgency == "high":
        return "high"

    if assessment.importance == "high" or assessment.urgency == "high":
        return "medium"

    return "low"


def determine_execution_mode(
    classification: Classification,
    risk_level: str
) -> str:
    if classification.task_type == "thought_leadership":
        if risk_level == "high":
            return "hybrid"
        return "sequential"

    if classification.task_type == "research":
        return "parallel"

    if classification.task_type == "content_transformation":
        return "hybrid"

    return "sequential"


def select_execution_route(
    classification: Classification,
    risk_level: str,
    review_policy
) -> List[str]:
    route = ["CEO Office"]

    if classification.primary_department not in route:
        route.append(classification.primary_department)

    if classification.task_type == "thought_leadership" and "Media Department" not in route:
        route.append("Media Department")

    if classification.task_type == "research" and "Research Department" not in route:
        route.append("Research Department")

    if review_policy.citation_required:
        route.append("Citation Verification")

    if review_policy.legal_required:
        route.append("Legal / Compliance")

    if review_policy.qa_required:
        route.append("QA")

    route.append("Output Workspace")

    # Remove duplicates while preserving order.
    cleaned_route = []
    for item in route:
        if item not in cleaned_route:
            cleaned_route.append(item)

    return cleaned_route


def generate_success_criteria(
    classification: Classification,
    priority: str
) -> List[str]:
    if classification.task_type == "thought_leadership":
        return [
            "Generate 3 LinkedIn post options.",
            "Preserve natural raw founder voice.",
            "Recommend the strongest option.",
            "Complete within the 30-minute daily workflow.",
            "Flag factual, legal, or reputation risk if detected."
        ]

    if classification.task_type == "research":
        return [
            "Summarize findings clearly.",
            "Separate facts from interpretation.",
            "Include sources if current/factual claims are used.",
            "Provide decision-useful insights."
        ]

    if classification.task_type == "finance":
        return [
            "State assumptions clearly.",
            "Calculate cost or runway logic transparently.",
            "Flag uncertainty.",
            "Provide executive recommendation."
        ]

    return [
        "Complete the user objective.",
        "Preserve original intent.",
        "Return clear and useful output."
    ]


def create_context_packet(
    task: Task,
    interpretation: Interpretation,
    user_context: Dict[str, Any]
) -> ContextPacket:
    return ContextPacket(
        id=new_id("ctx"),
        task_id=str(task.id),
        original_prompt=interpretation.raw_prompt,
        original_intent=interpretation.user_intent,
        project_context=task.project_id or user_context.get("active_project", "default"),
        founder_preferences=user_context.get("founder_preferences", {}),
        constraints={
            "daily_time_limit_minutes": user_context.get("daily_time_limit_minutes", 30),
            "voice": user_context.get("voice", "natural_raw"),
            "human_review_for_high_priority": True,
            "operating_ratio": "80_ai_20_human"
        }
    )


def create_execution_steps(
    task: Task,
    classification: Classification,
    route: List[str],
    priority: str,
    risk_level: str,
    execution_mode: str,
) -> List[ExecutionStep]:
    steps: List[ExecutionStep] = []
    previous_step_id = None

    for index, department in enumerate(route[1:], start=1):
        step_id = new_id("step")

        if department == "Media Department":
            objective = "Turn founder raw input into strong LinkedIn-ready options."
            expected_output = "3 draft options with recommendation."
            output_schema = {
                "drafts": "list[str]",
                "recommended_index": "int",
                "reason": "str"
            }

        elif department == "Research Department":
            objective = "Gather context or supporting insight."
            expected_output = "Research brief."
            output_schema = {
                "summary": "str",
                "key_points": "list[str]",
                "sources": "list[str]"
            }

        elif department == "Citation Verification":
            objective = "Verify factual or evidence-sensitive claims."
            expected_output = "Citation verification result."
            output_schema = {
                "verified_claims": "list[str]",
                "unsupported_claims": "list[str]",
                "recommendation": "str"
            }

        elif department == "Legal / Compliance":
            objective = "Review output for reputation, legal, and overclaim risk."
            expected_output = "Legal/compliance risk note."
            output_schema = {
                "risk_level": "str",
                "issues": "list[str]",
                "recommended_changes": "list[str]"
            }

        elif department == "QA":
            objective = "Improve clarity, structure, and output quality without over-polishing."
            expected_output = "QA-refined output."
            output_schema = {
                "refined_output": "str",
                "changes_made": "list[str]",
                "quality_score": "int"
            }

        elif department == "Output Workspace":
            objective = "Package final deliverable for approval or publishing."
            expected_output = "Final output package."
            output_schema = {
                "final_output": "str",
                "approval_required": "bool",
                "next_action": "str"
            }

        else:
            objective = f"Execute assigned work for {department}."
            expected_output = "Structured department output."
            output_schema = {"result": "str"}

        if execution_mode == "parallel" and department not in ["Output Workspace", "QA"]:
            depends_on = []
            can_run_parallel = True
        elif execution_mode == "hybrid" and department in ["Research Department", "Media Department"]:
            depends_on = []
            can_run_parallel = True
        else:
            depends_on = [previous_step_id] if previous_step_id else []
            can_run_parallel = False

        model_choice = choose_model_for_step(
            task_type=classification.task_type,
            department=department,
            output_format=classification.output_format,
            risk_level=risk_level
        )

        step = ExecutionStep(
            id=step_id,
            department=department,
            objective=objective,
            reason=f"{department} is required for {classification.task_type}.",
            expected_input="Context packet + previous step output where applicable.",
            expected_output=expected_output,
            output_schema=output_schema,
            depends_on=[dep for dep in depends_on if dep],
            can_run_parallel=can_run_parallel,
            estimated_time_minutes=5 if priority == "high" else 10,
            model_choice=model_choice,
            confidence_score=0.82
        )

        steps.append(step)
        previous_step_id = step_id

    return steps


def calculate_ceo_confidence(
    classification: Classification,
    risk_level: str,
    decision: str
) -> float:
    score = 0.80

    if classification.task_type == "general_execution":
        score -= 0.10

    if risk_level == "high":
        score -= 0.15

    if decision == "clarify":
        score -= 0.25

    return max(0.0, min(1.0, score))


async def ceo_engine(task: Task, user_context: Dict[str, Any]) -> CEOEngineResult:
    # 0. Semantic Memory Retrieval (The Chronicle)
    api_key = user_context.get("api_keys", {}).get("openai")
    memory_context = ""
    if api_key:
        try:
            # Generate embedding for the new prompt to search memory
            import openai
            client = openai.AsyncOpenAI(api_key=api_key)
            resp = await client.embeddings.create(
                input=[task.original_prompt.replace("\n", " ")],
                model="text-embedding-3-small"
            )
            query_emb = np.array(resp.data[0].embedding)
            
            # Search the chronicle
            similar_entries = chronicle.search(query_emb, limit=3)
            if similar_entries:
                memory_context = "\nRELEVANT PAST MISSIONS (MEMORY):\n"
                for entry in similar_entries:
                    meta = entry["metadata"]
                    memory_context += f"- [{meta['type']}] {meta['text_snippet']} (Score: {entry['score']:.2f})\n"
        except Exception as e:
            print(f"[CEO] Memory retrieval failed: {e}")

    interpretation = interpret_task(task.original_prompt + memory_context, user_context)

    classification = classify_task(
        interpretation=interpretation,
        project_context=task.project_id or user_context.get("active_project", "default")
    )

    strategic_assessment = assess_strategy(
        interpretation=interpretation,
        classification=classification,
        user_context=user_context
    )

    decision = make_decision(strategic_assessment, interpretation)
    priority = assign_priority(strategic_assessment)

    risk_details = assess_risk_from_text(interpretation.raw_prompt)
    risk_level = risk_details["risk_level"]

    # Krishna slider: 0 = cautious/defer more, 100 = aggressive/execute everything
    krishna_risk = int((user_context.get("character_risk_params") or {}).get("krishna", 50))
    if krishna_risk >= 70 and decision in ("schedule", "defer"):
        decision = "execute_now"
    elif krishna_risk <= 30 and decision == "execute_now":
        decision = "schedule"

    review_policy = decide_review_policy(
        risk_level=risk_level,
        priority=priority,
        risk_details=risk_details
    )

    # High Krishna risk = skip human intervention unless risk is truly high
    human_intervention = decide_human_intervention(
        risk_level=risk_level,
        priority=priority,
        decision=decision,
        review_policy=review_policy
    )
    if krishna_risk >= 80 and risk_level != "high":
        from app.models.orchestration import HumanIntervention
        human_intervention = HumanIntervention(required=False, reason=None)

    route = select_execution_route(
        classification=classification,
        risk_level=risk_level,
        review_policy=review_policy
    )

    execution_mode = determine_execution_mode(classification, risk_level)

    delegation_plan = create_execution_steps(
        task=task,
        classification=classification,
        route=route,
        priority=priority,
        risk_level=risk_level,
        execution_mode=execution_mode
    )

    success_criteria = generate_success_criteria(classification, priority)

    context_packet = create_context_packet(
        task=task,
        interpretation=interpretation,
        user_context=user_context
    )

    confidence = calculate_ceo_confidence(
        classification=classification,
        risk_level=risk_level,
        decision=decision
    )

    ceo_reasoning = (
        f"Task classified as {classification.task_type}. "
        f"Strategic fit is {strategic_assessment.strategic_fit}. "
        f"Decision is {decision}. "
        f"Risk level is {risk_level}. "
        f"Execution mode selected: {execution_mode}. "
        f"Krishna risk={krishna_risk} (governs decision aggression)."
    )

    return CEOEngineResult(
        task_id=str(task.id),
        interpretation=interpretation,
        classification=classification,
        strategic_assessment=strategic_assessment,
        decision=decision,
        priority=priority,
        risk_level=risk_level,
        execution_mode=execution_mode,
        route=route,
        success_criteria=success_criteria,
        context_packet=context_packet,
        delegation_plan=delegation_plan,
        review_policy=review_policy,
        human_intervention=human_intervention,
        ceo_reasoning=ceo_reasoning,
        confidence_score=confidence
    )
