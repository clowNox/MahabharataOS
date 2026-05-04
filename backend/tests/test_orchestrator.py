"""
tests/test_orchestrator.py
Tests the orchestration routing logic (CEO -> specific departments).
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from app.models.domain import Task
from app.engines.orchestrator import run_mahabharataos_task

@pytest.fixture
def mock_task():
    return Task(
        id="test-123",
        project_id="P-001",
        title="Test Task",
        original_prompt="Do something test related",
        context={}
    )

@pytest.fixture
def mock_context():
    return {
        "api_keys": {
            "openai": "fake-openai-key",
            "anthropic": "fake-claude-key",
            "tavily": "fake-tavily-key"
        }
    }


def test_orchestrator_routes_to_media(mock_task, mock_context):
    with patch("app.engines.ceo_engine_v2.call_openai") as mock_ceo_openai, \
         patch("app.engines.media_agent_v2.call_claude") as mock_media_claude, \
         patch("app.engines.media_agent_v2.call_openai") as mock_media_openai:
        
        mock_task.original_prompt = "Write a linkedin post about this test"
        
        # Mock CEO Interpretation
        mock_ceo_openai.return_value = json.dumps({
            "objective": "media", 
            "user_intent": "test", 
            "assumptions": []
        })

        # Mock Media Writing (Claude)
        mock_media_claude.return_value = "Draft 1 ---DRAFT_SEPARATOR--- Draft 2 ---DRAFT_SEPARATOR--- Draft 3"
        
        # Mock Hook (3 drafts) & Visual Suggestion (1) (OpenAI)
        mock_media_openai.side_effect = [
            "Hook 1", # hook for draft 1
            "Hook 2", # hook for draft 2
            "Hook 3", # hook for draft 3
            "TYPE: Abstract | PROMPT: A cool test image" # call for visual asset
        ]

        result = run_mahabharataos_task(mock_task, mock_context)
        
        assert "media" in result["outputs"]
        assert "visual_asset" in result["outputs"]["media"]
        assert result["outputs"]["media"]["visual_asset"]["type"] == "Abstract"
        assert len(result["outputs"]["media"]["draft_options"]) == 3


def test_orchestrator_routes_to_research(mock_task, mock_context):
    with patch("app.engines.ceo_engine_v2.call_openai") as mock_ceo_openai, \
         patch("app.engines.research_agent.call_openai") as mock_research_openai, \
         patch("app.engines.research_agent.call_claude") as mock_research_claude, \
         patch("app.engines.research_agent.web_search") as mock_search:
        
        mock_task.original_prompt = "Research the latest test data"

        # Mock CEO Interpretation
        mock_ceo_openai.return_value = json.dumps({
            "objective": "research", 
            "user_intent": "test", 
            "assumptions": []
        })

        # Mock Research Steps
        mock_research_openai.return_value = "latest test data query" # query gen
        mock_search.return_value = [{"title": "Source 1", "url": "http://test.com", "content": "data"}]
        mock_research_claude.return_value = "Synthesized research findings." # synthesis

        result = run_mahabharataos_task(mock_task, mock_context)
        
        assert "research" in result["outputs"]
        assert result["outputs"]["research"]["search_query"] == "latest test data query"
        assert result["outputs"]["research"]["results_count"] == 1
        assert "findings" in result["outputs"]["research"]


def test_orchestrator_routes_to_finance(mock_task, mock_context):
    with patch("app.engines.ceo_engine_v2.call_openai") as mock_ceo_openai, \
         patch("app.engines.finance_agent.call_claude") as mock_finance_claude, \
         patch("app.engines.finance_agent.call_openai") as mock_finance_openai:
        
        mock_task.original_prompt = "Calculate the budget cost for this test"

        # Mock CEO Interpretation
        mock_ceo_openai.return_value = json.dumps({
            "objective": "finance", 
            "user_intent": "test", 
            "assumptions": []
        })

        # Mock Finance Steps
        mock_finance_claude.return_value = "Narrative financial report." # strategic report
        mock_finance_openai.return_value = json.dumps({
            "line_items": [{"item": "Testing", "amount": 1000, "category": "QA"}],
            "totals": {"total_cost": 1000, "projected_revenue": 0},
            "risk_factors": ["Test risk"]
        }) # JSON extraction

        result = run_mahabharataos_task(mock_task, mock_context)
        
        assert "finance" in result["outputs"]
        assert "structured_data" in result["outputs"]["finance"]
        assert result["outputs"]["finance"]["structured_data"]["totals"]["total_cost"] == 1000
        assert len(result["outputs"]["finance"]["structured_data"]["line_items"]) == 1
