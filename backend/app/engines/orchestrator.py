import json
from typing import Dict, Any, Generator, AsyncGenerator
from app.models.domain import Task
from app.engines.ceo_engine_v2 import ceo_engine
from app.engines.delegation_engine_v2 import create_delegation_chain
from app.engines.media_agent_v2 import run_media_department
from app.engines.research_agent import run_research_department
from app.engines.finance_agent import run_finance_department
from app.engines.integrity_engine import run_vidura_audit
from app.models.orchestration import PipelineContext
from app.services.memory import chronicle


def _char_risk(user_context: Dict[str, Any], character_id: str, default: int = 50) -> int:
    """Returns 0-100 risk score for a character. 50 = neutral baseline."""
    params = user_context.get("character_risk_params", {})
    return int(params.get(character_id, default))


def run_mahabharataos_task(
    task: Task,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Synchronous orchestrator – retained for backward compatibility."""
    pipeline_ctx = PipelineContext(
        task=task,
        original_prompt=task.original_prompt,
        user_context=user_context,
    )
    import asyncio
    ceo_result = asyncio.run(ceo_engine(task, user_context))
    pipeline_ctx.ceo_result = ceo_result
    delegation_chain = create_delegation_chain(
        delegation_plan=ceo_result.delegation_plan,
        task_id=ceo_result.task_id,
        context_packet=ceo_result.context_packet,
    )
    # Execute departments (same logic as streaming, but without yielding)
    for dept in ceo_result.route:
        if dept in ["CEO Office", "Output Workspace"]:
            continue
        try:
            if dept == "Media Department":
                pipeline_ctx.department_outputs["media"] = run_media_department(
                    pipeline_ctx=pipeline_ctx,
                    arjuna_risk=_char_risk(user_context, "arjuna"),
                )
            elif dept == "Research Department":
                pipeline_ctx.department_outputs["research"] = run_research_department(
                    pipeline_ctx=pipeline_ctx,
                    drona_risk=_char_risk(user_context, "drona"),
                )
            elif dept in ["Finance & Capital Office", "Finance Department"]:
                pipeline_ctx.department_outputs["finance"] = run_finance_department(
                    pipeline_ctx=pipeline_ctx,
                    sahadeva_risk=_char_risk(user_context, "sahadeva"),
                )
            else:
                dept_key = dept.lower().replace(" ", "_")
                pipeline_ctx.department_outputs[dept_key] = {
                    "needs_human_approval": ceo_result.human_intervention.required,
                    "message": f"Task routed to {dept}. (Mock execution)",
                    "status": "completed",
                }
        except Exception as e:
            dept_key = dept.lower().replace(" ", "_")
            pipeline_ctx.errors.append(f"{dept} failed: {str(e)}")
            pipeline_ctx.department_outputs[dept_key] = {"error": str(e), "status": "failed"}
    # Vidura per‑department audits
    for dept, output_data in pipeline_ctx.department_outputs.items():
        if dept in ["vidura_audit"] or output_data.get("status") == "failed":
            continue
        audit_target = ""
        if dept == "media":
            audit_target = (output_data.get("recommendation") or {}).get("recommended_post", "")
        elif dept == "research":
            audit_target = output_data.get("findings", "")
        elif dept == "finance":
            audit_target = output_data.get("financial_breakdown", "")
        if audit_target:
            audit_result = run_vidura_audit(
                proposed_output=audit_target,
                output_type=dept,
                user_context=user_context,
                vidura_risk=_char_risk(user_context, "vidura"),
            )
            pipeline_ctx.vidura_audits[dept] = audit_result
    pipeline_ctx.department_outputs["vidura_audit"] = pipeline_ctx.vidura_audits
    return {
        "ceo_result": ceo_result,
        "delegation_chain": delegation_chain,
        "outputs": pipeline_ctx.department_outputs,
        "next_action": "human_approval" if ceo_result.human_intervention.required else "ready_for_review",
    }


async def stream_mahabharataos_task(
    task: Task,
    user_context: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """Yield incremental JSON events for each step of the pipeline.
    Uses async for semantic memory integration.
    """
    pipeline_ctx = PipelineContext(
        task=task,
        original_prompt=task.original_prompt,
        user_context=user_context,
    )
    api_key = user_context.get("api_keys", {}).get("openai")

    # 1️⃣ CEO step
    ceo_result = await ceo_engine(task, user_context)
    pipeline_ctx.ceo_result = ceo_result
    delegation_chain = create_delegation_chain(
        delegation_plan=ceo_result.delegation_plan,
        task_id=ceo_result.task_id,
        context_packet=ceo_result.context_packet,
    )
    
    # Store CEO strategic intent in memory
    if api_key:
        await chronicle.add_entry(
            text=f"Strategy for: {task.title}\nIntent: {ceo_result.intent}\nRoute: {ceo_result.route}",
            meta={"type": "strategy", "task_id": task.id, "character": "krishna"},
            api_key=api_key
        )

    yield f"data: {json.dumps({'step': 'ceo', 'result': ceo_result.__dict__}, default=str)}\n\n"

    # 2️⃣ Departments – stream each as it finishes
    for dept in ceo_result.route:
        if dept in ["CEO Office", "Output Workspace"]:
            continue
        try:
            out = None
            if dept == "Media Department":
                out = run_media_department(
                    pipeline_ctx=pipeline_ctx,
                    arjuna_risk=_char_risk(user_context, "arjuna"),
                )
                pipeline_ctx.department_outputs["media"] = out
                yield f"data: {json.dumps({'step': 'media', 'output': out}, default=str)}\n\n"
            elif dept == "Research Department":
                out = run_research_department(pipeline_ctx=pipeline_ctx)
                pipeline_ctx.department_outputs["research"] = out
                yield f"data: {json.dumps({'step': 'research', 'output': out}, default=str)}\n\n"
            elif dept in ["Finance & Capital Office", "Finance Department"]:
                out = run_finance_department(pipeline_ctx=pipeline_ctx)
                pipeline_ctx.department_outputs["finance"] = out
                yield f"data: {json.dumps({'step': 'finance', 'output': out}, default=str)}\n\n"
            else:
                dept_key = dept.lower().replace(" ", "_")
                out = {
                    "needs_human_approval": ceo_result.human_intervention.required,
                    "message": f"Task routed to {dept}. (Mock execution)",
                    "status": "completed",
                }
                pipeline_ctx.department_outputs[dept_key] = out
                yield f"data: {json.dumps({'step': dept_key, 'output': out}, default=str)}\n\n"
            
            # Store department output in memory
            if out and api_key and out.get("status") != "failed":
                await chronicle.add_entry(
                    text=str(out),
                    meta={"type": "department_output", "dept": dept, "task_id": task.id},
                    api_key=api_key
                )

        except Exception as e:
            dept_key = dept.lower().replace(" ", "_")
            pipeline_ctx.errors.append(f"{dept} failed: {str(e)}")
            out = {"error": str(e), "status": "failed"}
            pipeline_ctx.department_outputs[dept_key] = out
            yield f"data: {json.dumps({'step': dept_key, 'error': str(e)}, default=str)}\n\n"

    # 3️⃣ Vidura audits
    for dept, output_data in pipeline_ctx.department_outputs.items():
        if dept == "vidura_audit" or output_data.get("status") == "failed":
            continue
        audit_target = ""
        if dept == "media":
            audit_target = (output_data.get("recommendation") or {}).get("recommended_post", "")
        elif dept == "research":
            audit_target = output_data.get("findings", "")
        elif dept == "finance":
            audit_target = output_data.get("financial_breakdown", "")
        if audit_target:
            audit_result = run_vidura_audit(
                proposed_output=audit_target,
                output_type=dept,
                user_context=user_context,
                vidura_risk=_char_risk(user_context, "vidura"),
            )
            pipeline_ctx.vidura_audits[dept] = audit_result
            
            # Store audit result in memory
            if api_key:
                await chronicle.add_entry(
                    text=f"Audit for {dept}: {audit_result.integrity_score}% - {audit_result.moral_judgment}",
                    meta={"type": "audit", "dept": dept, "task_id": task.id, "character": "vidura"},
                    api_key=api_key
                )
            
            yield f"data: {json.dumps({'step': f'vidura_{dept}', 'audit': audit_result}, default=str)}\n\n"

    # Final payload
    final = {
        "ceo_result": ceo_result,
        "delegation_chain": delegation_chain,
        "outputs": pipeline_ctx.department_outputs,
        "next_action": "human_approval" if ceo_result.human_intervention.required else "ready_for_review",
    }
    yield f"data: {json.dumps({'step': 'final', 'result': final}, default=str)}\n\n"
