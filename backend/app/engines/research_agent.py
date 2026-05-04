"""
research_agent.py
Handles tasks assigned to the Research Department.
Extracts insights and summaries from the provided context.
"""
from typing import Dict, Any
from app.models.domain import Task
from app.models.orchestration import PipelineContext
from app.engines.model_router import choose_model_for_step, call_openai, call_claude, call_gemini
from app.tools.tavily_search import web_search, format_search_results


def run_research_department(
    pipeline_ctx: PipelineContext,
    drona_risk: int = 50,
) -> Dict[str, Any]:
    """
    Executes the research step with real web searching.
    """
    task = pipeline_ctx.task
    user_context = pipeline_ctx.user_context
    api_keys = user_context.get("api_keys", {})
    openai_key = api_keys.get("openai")
    anthropic_key = api_keys.get("anthropic")
    gemini_key = api_keys.get("gemini")
    tavily_key = api_keys.get("tavily")

    # Step 1: Generate a search query based on the task
    query_prompt = f"""
    Based on the following task, generate a single, highly effective search query to find the most relevant and up-to-date information.
    
    Task Title: {task.title}
    Objective: {task.original_prompt}
    
    Output only the search query string.
    """
    
    query = call_openai(query_prompt, "You are a search query optimizer.", openai_key)
    if "MOCK:" in query:
        # Fallback if OpenAI key is missing for query generation
        query = task.title if task.title else task.original_prompt

    # Step 2: Perform the web search
    search_results = web_search(query, api_key=tavily_key)
    formatted_results = format_search_results(search_results)

    # Step 3: Synthesize the findings
    # Drona slider influences research depth and skepticism
    depth_instruction = "Focus on high-level summaries and key insights."
    if drona_risk >= 70:
        depth_instruction = "Perform deep-dive analysis. Be skeptical of sources and look for hidden patterns or contrary evidence."
    elif drona_risk <= 30:
        depth_instruction = "Provide a fast, high-level summary of the most obvious facts."

    system_prompt = (
        "You are Drona, the Master Teacher and Lead Researcher for MahabharataOS. "
        f"{depth_instruction} "
        "Synthesize results into a professional research brief. "
        "Focus on actionable data points. "
        "Output in markdown."
    )

    prompt = f"""
    Objective: {task.original_prompt}
    Title: {task.title}
    Context Packet: {pipeline_ctx.ceo_result.context_packet.__dict__ if pipeline_ctx.ceo_result else {}}
    
    Web Search Results for "{query}":
    {formatted_results}
    
    Please provide a structured research brief based on the above information.
    """

    model = choose_model_for_step(
        task_type="research",
        department="Research Department",
        output_format="document",
        risk_level="low"
    )

    if model == "claude" and anthropic_key:
        response = call_claude(prompt, system_prompt, anthropic_key)
    elif model == "gemini" and gemini_key:
        response = call_gemini(prompt, system_prompt, gemini_key)
    else:
        response = call_openai(prompt, system_prompt, openai_key)

    if "MOCK:" in response and not (openai_key or anthropic_key or gemini_key):
        response = f"MOCK: Research findings for '{query}'. (API key missing for synthesis, but search returned {len(search_results)} results)"

    return {
        "needs_human_approval": False,
        "search_query": query,
        "results_count": len(search_results),
        "findings": response,
        "raw_model_used": model
    }
