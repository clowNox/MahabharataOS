from typing import Dict, Any, List
from app.models.orchestration import RiskLevel, ReviewPolicy, HumanIntervention


HIGH_RISK_TERMS = [
    "guarantee",
    "always",
    "never",
    "fraud",
    "scam",
    "illegal",
    "lawsuit",
    "definitely",
    "must",
    "will 100%",
    "expose",
    "attack",
]

FACTUAL_MARKERS = [
    "%",
    "data",
    "study",
    "report",
    "research",
    "according to",
    "latest",
    "current",
    "market size",
    "statistics",
    "survey",
    "evidence",
]

REPUTATION_MARKERS = [
    "controversial",
    "call out",
    "criticize",
    "blame",
    "public response",
    "reply publicly",
    "defend",
]


def detect_markers(text: str, markers: List[str]) -> List[str]:
    lower = text.lower()
    return [marker for marker in markers if marker in lower]


def assess_risk_from_text(text: str) -> Dict[str, Any]:
    high_hits = detect_markers(text, HIGH_RISK_TERMS)
    factual_hits = detect_markers(text, FACTUAL_MARKERS)
    reputation_hits = detect_markers(text, REPUTATION_MARKERS)

    if high_hits or reputation_hits:
        level: RiskLevel = "high"
    elif factual_hits:
        level = "medium"
    else:
        level = "low"

    return {
        "risk_level": level,
        "high_risk_markers": high_hits,
        "factual_markers": factual_hits,
        "reputation_markers": reputation_hits,
    }


def decide_review_policy(
    risk_level: RiskLevel,
    priority: str,
    risk_details: Dict[str, Any]
) -> ReviewPolicy:
    reasons: List[str] = []

    qa_required = False
    legal_required = False
    citation_required = False
    human_review_required = False

    if risk_level == "high":
        qa_required = True
        legal_required = True
        human_review_required = True
        reasons.append("High-risk or reputation-sensitive language detected.")

    if risk_details.get("factual_markers"):
        citation_required = True
        reasons.append("Factual or evidence-sensitive claim detected.")

    if priority == "high":
        human_review_required = True
        reasons.append("High-priority task requires human approval.")

    if risk_level == "medium":
        qa_required = True
        reasons.append("Medium-risk task requires QA review.")

    return ReviewPolicy(
        qa_required=qa_required,
        legal_required=legal_required,
        citation_required=citation_required,
        human_review_required=human_review_required,
        reasons=reasons
    )


def decide_human_intervention(
    risk_level: RiskLevel,
    priority: str,
    decision: str,
    review_policy: ReviewPolicy
) -> HumanIntervention:
    if decision == "clarify":
        return HumanIntervention(
            required=True,
            reason="Clarification required before execution."
        )

    if review_policy.human_review_required:
        return HumanIntervention(
            required=True,
            reason="Human review required due to priority or risk level."
        )

    return HumanIntervention(required=False, reason=None)
