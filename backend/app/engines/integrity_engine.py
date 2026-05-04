import json
from typing import Dict, Any
from app.engines.model_router import call_openai


def run_vidura_audit(
    proposed_output: str,
    output_type: str,
    user_context: Dict[str, Any] = None,
    vidura_risk: int = 50,
) -> Dict[str, Any]:
    """
    Vidura Audit: Performs a strategic and ethical critique of proposed outputs.
    vidura_risk 0-100: 0 = lenient/fast approval, 100 = strict/thorough scrutiny.
    """

    # Vidura slider: shapes how hard Vidura pushes back
    if vidura_risk >= 70:
        strictness_instruction = (
            "You are in HIGH SCRUTINY mode. Be rigorous and unforgiving. "
            "Flag every ambiguous claim, overclaim, or reputation risk. "
            "Set is_safe_to_deploy=false unless the output is near-flawless. "
            "Your integrity_score should reflect real risk — don't inflate it."
        )
    elif vidura_risk <= 30:
        strictness_instruction = (
            "You are in LIGHT REVIEW mode. Be supportive and pragmatic. "
            "Flag only clear factual errors or serious legal/reputation risks. "
            "Minor stylistic issues are not warnings. "
            "Approve confidently if there are no material concerns."
        )
    else:
        strictness_instruction = (
            "You are in BALANCED mode. Flag genuine risks but don't nitpick. "
            "Focus on strategic alignment and material reputation risks."
        )

    system_prompt = f"""You are Vidura, the Sage of Ethics and Strategy for MahabharataOS.
Your role is to audit the following {output_type} draft.
{strictness_instruction}

Evaluate for:
1. Strategic Alignment: Does it achieve the mission?
2. Reputation Risk: Does it sound arrogant, fake, or legally dangerous?
3. Logical Integrity: Are the claims consistent?

Output ONLY valid JSON in this format:
{{
    "integrity_score": int,
    "assessment": "Short summary of your audit",
    "warnings": ["Warning 1", "Warning 2"],
    "is_safe_to_deploy": bool
}}"""

    prompt = f"PROPOSED OUTPUT FOR AUDIT:\n\n{proposed_output}"

    api_keys = (user_context or {}).get("api_keys", {})
    openai_key = api_keys.get("openai")

    response = call_openai(prompt, system_prompt, openai_key)

    if "MOCK:" in response:
        # Fallback score reflects Vidura's strictness level
        mock_score = max(40, 95 - vidura_risk // 2)
        return {
            "integrity_score": mock_score,
            "assessment": f"Vidura audit (mock, strictness={vidura_risk}): Strategic alignment is strong.",
            "warnings": ["Ensure citations for secondary data are verified before posting."],
            "is_safe_to_deploy": mock_score >= 60,
        }

    try:
        clean_json = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {
            "integrity_score": 50,
            "assessment": f"Audit failed to parse: {str(e)}",
            "warnings": ["System integrity check bypassed due to technical error."],
            "is_safe_to_deploy": False,
        }
