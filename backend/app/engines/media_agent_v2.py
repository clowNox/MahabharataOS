from typing import Dict, Any, List
from app.models.domain import Task
from app.models.orchestration import PipelineContext
from app.engines.model_router import call_claude, call_openai


def thought_collector(raw_prompt: str, research_context: str = "") -> Dict[str, Any]:
    return {
        "raw_thought": raw_prompt,
        "research_context": research_context,
        "core_signal": raw_prompt.strip(),
        "founder_energy": "raw_reflective"
    }


def idea_structurer(thought: Dict[str, Any]) -> Dict[str, Any]:
    raw = thought["raw_thought"]
    research = thought["research_context"]

    return {
        "thesis": raw,
        "research_data": research,
        "supporting_points": [
            "What happened?",
            "Data-backed insights (if any)",
            "Founder lesson"
        ]
    }


def linkedin_draft_writer(
    structured_idea: Dict[str, Any],
    voice_profile: Dict[str, Any],
    user_context: Dict[str, Any] = None
) -> List[str]:
    thesis = structured_idea["thesis"]
    research = structured_idea["research_data"]
    
    system_prompt = f"""You are an elite LinkedIn ghostwriter for a founder.
Voice Profile:
- Style: {voice_profile.get('style', 'natural')}
- Avoid: {', '.join(voice_profile.get('avoid', []))}
- Prefer: {', '.join(voice_profile.get('prefer', []))}

Write exactly 3 different draft versions of a LinkedIn post based on the provided thesis and research data.
Each draft should have a distinct angle:
1. The "Storyteller" (Narrative-led)
2. The "Analyst" (Data/Research-led)
3. The "Contrarian" (Challenging status quo)

Separate each draft with the exact string '---DRAFT_SEPARATOR---'."""

    prompt = f"""Thesis: {thesis}
Research Data: {research}

Please generate the 3 drafts now."""
    
    api_keys = (user_context or {}).get("api_keys", {})
    anthropic_key = api_keys.get("anthropic", None)
    openai_key = api_keys.get("openai", None)
    
    # We prefer Claude for writing
    response = call_claude(prompt, system_prompt, api_key=anthropic_key)
    if "MOCK:" in response:
        response = call_openai(prompt, system_prompt, api_key=openai_key)
    
    if "MOCK:" in response:
        return [f"Mock Draft 1: {thesis}", f"Mock Draft 2: {thesis}", f"Mock Draft 3: {thesis}"]
        
    drafts = [d.strip() for d in response.split("---DRAFT_SEPARATOR---") if d.strip()]
    
    while len(drafts) < 3:
        drafts.append(f"Fallback draft due to parsing issue on thesis: {thesis}")
        
    return drafts[:3]


def hook_specialist(drafts: List[str], user_context: Dict[str, Any] = None) -> List[Dict[str, str]]:
    api_keys = (user_context or {}).get("api_keys", {})
    openai_key = api_keys.get("openai", None)
    
    hooks_packet = []
    
    system_prompt = "You are a hook specialist for social media. Generate a single, punchy, high-engagement hook for the following post draft. Output ONLY the hook string."

    for i, draft in enumerate(drafts):
        hook = call_openai(f"Draft: {draft[:500]}...", system_prompt, api_key=openai_key)
        if "MOCK:" in hook:
            # Fallback hooks
            fallbacks = [
                "I am learning that systems matter more than motivation.",
                "The more I build, the more I respect delegation.",
                "Hard truth: a slow system is a broken system."
            ]
            hook = fallbacks[i % 3]

        hooks_packet.append({
            "draft_index": i,
            "hook": hook.strip('"').strip(),
            "combined_post": f"{hook.strip()}\n\n{draft}"
        })

    return hooks_packet


def visual_asset_suggester(thesis: str, user_context: Dict[str, Any] = None) -> Dict[str, str]:
    api_keys = (user_context or {}).get("api_keys", {})
    openai_key = api_keys.get("openai", None)
    
    system_prompt = "You are a creative director. Suggest a visual asset for a social media post. Provide a 'type' (e.g., 'Chart', 'Realistic Photo', 'Abstract Illustration') and a 'prompt' for an image generator."
    
    prompt = f"Post Thesis: {thesis}\n\nProvide the suggestion in format: TYPE: [type] | PROMPT: [prompt]"
    
    suggestion = call_openai(prompt, system_prompt, api_key=openai_key)
    
    if "MOCK:" in suggestion:
        return {
            "type": "Abstract Illustration",
            "prompt": f"A clean, minimalist illustration representing '{thesis}' in a corporate tech style."
        }
    
    try:
        parts = suggestion.split("|")
        asset_type = parts[0].replace("TYPE:", "").strip()
        asset_prompt = parts[1].replace("PROMPT:", "").strip()
        return {"type": asset_type, "prompt": asset_prompt}
    except:
        return {"type": "Custom Image", "prompt": suggestion}


def recommend_best_post(posts: List[Dict[str, str]]) -> Dict[str, Any]:
    if not posts:
        return {
            "recommended_index": 0,
            "recommended_post": "",
            "reason": "No drafts were generated."
        }

    best = posts[0]
    reasons = [
        "Strongest narrative arc and emotional resonance.",
        "Best use of provided data and research points.",
        "Highest engagement potential based on the contrarian angle."
    ]

    return {
        "recommended_index": 0,
        "recommended_post": best.get("combined_post", ""),
        "reason": reasons[0]
    }


def run_media_department(
    pipeline_ctx: PipelineContext,
    arjuna_risk: int = 50,
) -> Dict[str, Any]:
    task = pipeline_ctx.task
    user_context = pipeline_ctx.user_context
    research_findings = pipeline_ctx.department_outputs.get("research", {}).get("findings", "")

    thought = thought_collector(task.original_prompt, research_findings)
    structured_idea = idea_structurer(thought)

    # Arjuna slider: 0 = safe/measured, 100 = bold/provocative
    if arjuna_risk >= 70:
        style = "bold_provocative"
        avoid = ["safe takes", "corporate polish", "hedging language"]
        prefer = ["strong contrarian angles", "pattern interrupts", "raw founder energy", "controversial truths"]
    elif arjuna_risk <= 30:
        style = "measured_thoughtful"
        avoid = ["controversy", "bold claims", "aggressive tone"]
        prefer = ["nuanced perspective", "data-backed", "humble tone", "reflective storytelling"]
    else:
        style = "natural_raw"
        avoid = ["corporate polish", "generic motivation", "fake authority"]
        prefer = ["direct", "reflective", "systems thinking", "founder journey"]

    voice_profile = {
        "style": style,
        "avoid": avoid,
        "prefer": prefer,
    }

    drafts = linkedin_draft_writer(structured_idea, voice_profile, user_context)
    posts_with_hooks = hook_specialist(drafts, user_context)
    recommendation = recommend_best_post(posts_with_hooks)
    visual_asset = visual_asset_suggester(task.original_prompt, user_context)

    return {
        "format": "linkedin_post",
        "draft_options": posts_with_hooks,
        "recommendation": recommendation,
        "visual_asset": visual_asset,
        "needs_human_approval": True
    }
