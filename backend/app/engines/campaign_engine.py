from typing import List, Dict, Any
import json
from app.engines.model_router import call_openai

def generate_campaign_plan(theme: str, duration_days: int, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Takes a high-level campaign theme and breaks it down into daily task objectives.
    """
    system_prompt = f"""You are the Strategic Campaign Planner for MahabharataOS.
    Break down the user's theme into {duration_days} distinct daily LinkedIn post objectives.
    Each day should have a specific angle and build on the previous day's narrative.
    
    IMPORTANT: Every 'prompt' you generate MUST start with the phrase 'Draft a LinkedIn post about...' to ensure the orchestrator routes it to the Media Department.
    
    Output ONLY valid JSON in this exact format:
    [
        {{
            "day": 1,
            "title": "Short Descriptive Title",
            "prompt": "Draft a LinkedIn post about [specific daily objective]..."
        }}
    ]
    """
    
    prompt = f"Campaign Theme: {theme}\nDuration: {duration_days} days."
    
    api_keys = user_context.get("api_keys", {})
    openai_key = api_keys.get("openai")
    
    response = call_openai(prompt, system_prompt, openai_key)
    
    if "MOCK:" in response:
        # Fallback for mock environment
        return [
            {
                "day": i + 1,
                "title": f"Day {i+1}: {theme} Insight",
                "prompt": f"Research and draft a post about {theme} focusing on aspect {i+1}."
            }
            for i in range(duration_days)
        ]
    
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        plan = json.loads(clean_json)
        return plan
    except Exception as e:
        print(f"Failed to parse campaign JSON: {e}")
        return [{"day": 1, "title": "Error", "prompt": f"Failed to generate plan: {str(e)}"}]
