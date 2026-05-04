from typing import Dict, Any, List
import json
from app.models.domain import Task
from app.models.orchestration import PipelineContext
from app.engines.model_router import choose_model_for_step, call_openai, call_claude


def run_finance_department(
    pipeline_ctx: PipelineContext,
    sahadeva_risk: int = 50,
) -> Dict[str, Any]:
    """
    Executes the finance step with structured data extraction.
    """
    task = pipeline_ctx.task
    user_context = pipeline_ctx.user_context
    api_keys = user_context.get("api_keys", {})
    openai_key = api_keys.get("openai")
    anthropic_key = api_keys.get("anthropic")

    # Step 1: Narrative Analysis (Claude is usually better for nuanced CFO advice)
    # Sahadeva slider influences financial optimism vs caution
    outlook_instruction = "Provide a balanced CFO narrative."
    if sahadeva_risk >= 70:
        outlook_instruction = "Provide a highly cautious, risk-averse CFO narrative. Focus on potential losses and capital preservation."
    elif sahadeva_risk <= 30:
        outlook_instruction = "Provide an optimistic CFO narrative. Focus on growth potential and aggressive ROI targets."

    narrative_system = (
        "You are Sahadeva, the CFO of MahabharataOS. "
        f"{outlook_instruction} "
        "Analyze objectives and provide a strategic CFO narrative. "
        "Focus on ROI, capital allocation, and growth. "
        "Output in clean markdown."
    )
    
    narrative_prompt = f"""
    Objective: {task.original_prompt}
    Context: {pipeline_ctx.ceo_result.context_packet.__dict__ if pipeline_ctx.ceo_result else {}}
    Please provide a high-level strategic financial report.
    """
    
    narrative = call_claude(narrative_prompt, narrative_system, anthropic_key)
    if "MOCK:" in narrative:
        narrative = call_openai(narrative_prompt, narrative_system, openai_key)

    # Step 2: Structured Data Extraction (GPT-4o is excellent for JSON)
    json_system = (
        "You are a financial data extractor. "
        "Extract the financial line items from the user's objective and context. "
        "Ensure all math is double-checked and accurate. "
        "Output ONLY valid JSON in this format: "
        "{ \"line_items\": [{ \"item\": \"string\", \"amount\": number, \"category\": \"string\" }], \"totals\": { \"total_cost\": number, \"projected_revenue\": number }, \"risk_factors\": [\"string\"] }"
    )
    
    json_prompt = f"Objective: {task.original_prompt}\\nContext: {pipeline_ctx.ceo_result.context_packet.__dict__ if pipeline_ctx.ceo_result else {}}"
    
    json_response = call_openai(json_prompt, json_system, openai_key)
    
    structured_data = {
        "line_items": [],
        "totals": {"total_cost": 0, "projected_revenue": 0},
        "risk_factors": ["High uncertainty due to lack of historical data."]
    }

    try:
        # Simple cleanup if the LLM includes markdown backticks
        clean_json = json_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        extracted = json.loads(clean_json)
        structured_data.update(extracted)
    except Exception as e:
        print(f"Failed to parse finance JSON: {e}")
        # Use simple fallback if JSON fails
        if "MOCK:" not in json_response:
             structured_data["risk_factors"].append("Structured data extraction failed.")

    return {
        "needs_human_approval": True,
        "financial_breakdown": narrative,
        "structured_data": structured_data,
        "raw_model_used": "claude-3.5-sonnet + gpt-4o"
    }
