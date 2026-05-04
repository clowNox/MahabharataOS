import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

from google import genai as google_genai

load_dotenv()

def call_openai(prompt: str, system_prompt: str = "", api_key: str = None) -> str:
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key or key.startswith("sk-proj-...") or "..." in key:
        return "MOCK: OpenAI API Key not found or invalid. Please provide a valid key."
    
    try:
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"MOCK: OpenAI API call failed: {str(e)}"

def call_claude(prompt: str, system_prompt: str = "", api_key: str = None) -> str:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key or key.startswith("sk-ant-...") or "..." in key:
        return "MOCK: Anthropic API Key not found or invalid. Please provide a valid key."
        
    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.content[0].text
    except Exception as e:
        return f"MOCK: Anthropic API call failed: {str(e)}"

def call_gemini(prompt: str, system_prompt: str = "", api_key: str = None) -> str:
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return "MOCK: Gemini API Key not found. Please provide a valid key."

    try:
        client = google_genai.Client(api_key=key)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"MOCK: Gemini API call failed: {str(e)}"

def choose_model_for_step(
    task_type: str,
    department: str,
    output_format: str,
    risk_level: str,
    cost_preference: str = "balanced"
) -> str:
    """
    Selects the best AI model/tool for a step.
    """

    if department == "Research Department":
        # We use Claude for synthesis because it handles complex context packets best
        return "claude"

    if department == "Media Department":
        if output_format in ["linkedin_post", "document", "longform"]:
            return "claude"
        return "chatgpt"

    if department == "Citation Verification":
        return "gemini" # Gemini is good at checking facts against context

    if department == "Legal / Compliance":
        return "claude"

    if department == "QA":
        return "chatgpt"

    if department == "Technology & Systems":
        return "chatgpt"

    if task_type == "trend_pulse":
        return "gemini"

    if cost_preference == "low":
        return "gemini"

    return "chatgpt"


def model_reason(model: str) -> str:
    reasons = {
        "chatgpt": "Strong general execution and structured reasoning.",
        "claude": "Strong for long-form writing, tone refinement, and nuanced synthesis.",
        "perplexity": "Best suited for live research (external tool).",
        "gemini": "High context window and strong factual reasoning.",
        "grok": "Useful for cultural pulse and real-time sentiment tasks."
    }

    return reasons.get(model, "Default model selected.")
