import pytest
import json
from unittest.mock import MagicMock
from backend.ai.agents import BaseAgent, ConsensusAgent, AgentState

def test_missing_llm_provider_returns_unavailable():
    agent = ConsensusAgent()
    agent.llm = None  # Simulate missing/unavailable LLM provider

    state: AgentState = {
        "symbol": "RELIANCE",
        "regime": "BULLISH",
        "technical_data": {"indicators": {"last_price": 2500.0}},
        "fundamental_data": {},
        "news_sentiment": {},
        "macro_data": {},
        "institutional_data": {},
        "options_data": {},
        "earnings_data": {},
        "feature_vector": {},
        "recommendations": [],
        "consensus": ""
    }

    res_state = agent.analyze(state)
    consensus_data = json.loads(res_state["consensus"])

    assert consensus_data["status"] == "UNAVAILABLE"
    assert consensus_data["rating"] == "UNAVAILABLE"
    assert consensus_data["conviction"] == 0
    assert consensus_data["target"] is None
    assert consensus_data["stop_loss"] is None
    assert consensus_data["risk_reward"] is None
    assert consensus_data["entry"] == 2500.0

def test_unknown_current_price_does_not_fabricate_zero():
    agent = ConsensusAgent()
    agent.llm = None

    state: AgentState = {
        "symbol": "RELIANCE",
        "regime": "NEUTRAL",
        "technical_data": {"indicators": {"last_price": "Unknown"}},
        "fundamental_data": {},
        "news_sentiment": {},
        "macro_data": {},
        "institutional_data": {},
        "options_data": {},
        "earnings_data": {},
        "feature_vector": {},
        "recommendations": [],
        "consensus": ""
    }

    res_state = agent.analyze(state)
    consensus_data = json.loads(res_state["consensus"])

    assert consensus_data["entry"] is None
    assert consensus_data["target"] is None
    assert consensus_data["stop_loss"] is None

def test_llm_invocation_failure_returns_unavailable():
    agent = ConsensusAgent()
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("API connection timeout")
    agent.llm = mock_llm

    state: AgentState = {
        "symbol": "INFY",
        "regime": "BULLISH",
        "technical_data": {"indicators": {"last_price": 1500.0}},
        "fundamental_data": {},
        "news_sentiment": {},
        "macro_data": {},
        "institutional_data": {},
        "options_data": {},
        "earnings_data": {},
        "feature_vector": {},
        "recommendations": [],
        "consensus": ""
    }

    res_state = agent.analyze(state)
    consensus_data = json.loads(res_state["consensus"])

    assert consensus_data["status"] == "UNAVAILABLE"
    assert consensus_data["rating"] == "UNAVAILABLE"
    assert consensus_data["target"] is None
    assert consensus_data["stop_loss"] is None

def test_successful_provider_response():
    agent = ConsensusAgent()
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"rating": "BUY", "conviction": 85, "entry": 1500.0, "target": 1620.0, "stop_loss": 1440.0, "thesis": "Strong momentum"}'
    mock_llm.invoke.return_value = mock_response
    agent.llm = mock_llm

    state: AgentState = {
        "symbol": "INFY",
        "regime": "BULLISH",
        "technical_data": {"indicators": {"last_price": 1500.0}},
        "fundamental_data": {},
        "news_sentiment": {},
        "macro_data": {},
        "institutional_data": {},
        "options_data": {},
        "earnings_data": {},
        "feature_vector": {},
        "recommendations": [],
        "consensus": ""
    }

    res_state = agent.analyze(state)
    consensus_data = json.loads(res_state["consensus"])

    assert consensus_data["rating"] == "BUY"
    assert consensus_data["conviction"] == 85
    assert consensus_data["target"] == 1620.0
    assert consensus_data["stop_loss"] == 1440.0
