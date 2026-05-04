from typing import Dict, Any, List
from app.models.domain import Task
from app.engines.model_router import model_router, call_model

def thought_collector(raw_thought: str) -> str:
    """Passes raw thought through initial capture agent."""
    prompt = f"Extract the core thesis from this raw thought: {raw_thought}"
    model = model_router("general_execution")
    return call_model(model, prompt)

def idea_structurer(thesis: str) -> str:
    """Structures the idea into a logical flow."""
    prompt = f"Structure this thesis into a 3-part framework (Truth, Implementation, Outcome): {thesis}"
    model = model_router("thought_leadership")
    return call_model(model, prompt)

def linkedin_draft_writer(structured_idea: str, voice_profile: str) -> str:
    """Writes the first draft."""
    prompt = f"Write a LinkedIn post using this structure: {structured_idea}. Apply this voice profile: {voice_profile}"
    model = model_router("longform_writing")
    return call_model(model, prompt)

def founder_voice_editor(draft: str) -> str:
    """Refines the text to sound like a natural founder."""
    prompt = f"Edit this draft to remove generic AI fluff and make it sound like a raw founder talking: {draft}"
    model = model_router("thought_leadership")
    return call_model(model, prompt)

def hook_specialist(draft: str) -> str:
    """Generates strong hooks."""
    prompt = f"Generate 3 scroll-stopping hooks for this draft: {draft}"
    model = model_router("thought_leadership")
    return call_model(model, prompt)

def run_media_department(task: Task, delegation_chain: List[Any]) -> Dict[str, str]:
    """
    Main pipeline for the Media Department.
    Runs the specific agents in sequence.
    """
    print("[Media Department] Starting thought leadership pipeline...")
    
    # 1. Capture & Structure
    thesis = thought_collector(task.original_prompt)
    structured_idea = idea_structurer(thesis)
    
    # 2. Draft & Voice
    mock_voice_profile = "Direct, no fluff, systems-thinker, authentic."
    draft = linkedin_draft_writer(structured_idea, mock_voice_profile)
    voiced_draft = founder_voice_editor(draft)
    
    # 3. Final Polish
    hooks = hook_specialist(voiced_draft)
    
    return {
        "final_draft": voiced_draft,
        "recommended_hooks": hooks,
        "format": "text_post"
    }
