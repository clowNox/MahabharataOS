from typing import Dict, Any

def check_clarity(output: str) -> int:
    """Scores clarity from 1-10."""
    return 8

def detect_ai_generic(output: str) -> bool:
    """Flags if the text uses overused AI words like 'delve', 'tapestry', 'testament'."""
    ai_words = ["delve", "tapestry", "testament", "in today's fast-paced", "unlock"]
    return any(word in output.lower() for word in ai_words)

def remove_generic_language(output: str) -> str:
    """Cleans up the text."""
    # In reality, this uses an LLM call to rewrite
    return output.replace("delve", "look").replace("tapestry", "system")

def citation_required(output: str) -> bool:
    """Checks if claims require fact-checking."""
    factual_markers = ["%", "study", "report", "data", "research", "according to", "latest"]
    return any(marker in output.lower() for marker in factual_markers)

def legal_review_required(output: str) -> bool:
    """Checks if text contains risky language."""
    risky_terms = ["guarantee", "always", "never", "illegal", "fraud", "scam", "must"]
    return any(term in output.lower() for term in risky_terms)

def run_qa_light(output: str) -> Dict[str, Any]:
    """
    Lightweight QA pipeline that doesn't slow down the system.
    """
    print("[QA Agent] Running light quality checks...")
    
    is_generic = detect_ai_generic(output)
    if is_generic:
        output = remove_generic_language(output)
        
    return {
        "refined_output": output,
        "metrics": {
            "clarity_score": check_clarity(output),
            "ai_fluff_detected": is_generic,
            "needs_citation": citation_required(output),
            "needs_legal": legal_review_required(output)
        }
    }
