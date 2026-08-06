from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from backend.core.config import settings
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    agent_name: str
    signal: str # BUY, SELL, HOLD
    confidence: float # 0-1
    reasons: List[str]
    risks: List[str]
    supporting_evidence: Dict[str, Any]

class AgentState(TypedDict):
    symbol: str
    technical_data: dict
    fundamental_data: dict
    news_sentiment: dict
    macro_data: dict
    institutional_data: dict
    options_data: dict
    earnings_data: dict
    feature_vector: dict
    recommendations: List[AgentResponse]
    consensus: str

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        # Diagnostic Check for API Key
        key = settings.GROQ_API_KEY
        if not key or key == "YOUR_GROQ_API_KEY":
             raise ValueError("GROQ_API_KEY not configured in environment variables.")

        # Log key availability (safe prefix only)
        print(f"Agent {name} initialized with key prefix: {key[:8]}...")

        # Using Llama 3.3 70B on Groq
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )

    def get_structured_prompt(self, context: str) -> str:
        return f"""
        You are a highly experienced institutional {self.name} analyst.
        Context: {context}

        Analyze the provided data and return a structured JSON response EXACTLY in this format:
        {{
            "agent_name": "{self.name}",
            "signal": "BUY | SELL | HOLD",
            "confidence": 0.0 to 1.0,
            "reasons": ["reason 1", "reason 2"],
            "risks": ["risk 1", "risk 2"],
            "supporting_evidence": {{"metric_name": "value"}},
            "moat_rating": "WIDE | NARROW | NONE",
            "management_score": 0.0 to 5.0
        }}
        """

class TechnicalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Technical indicators and SMC data for {state['symbol']}: {state['technical_data']}")
        response = self.llm.invoke(prompt)
        try:
            import json
            data = json.loads(response.content)
            state['recommendations'].append(AgentResponse(**data))
        except:
            state['recommendations'].append(AgentResponse(agent_name="Technical", signal="HOLD", confidence=0, reasons=["Parsing error"], risks=[], supporting_evidence={}))
        return state

class ICTAgent(BaseAgent):
    def __init__(self):
        super().__init__("ICT")

    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"ICT Concepts (Liquidity, Gaps, Killzones) for {state['symbol']}: {state['technical_data'].get('ict', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class WyckoffAgent(BaseAgent):
    def __init__(self):
        super().__init__("Wyckoff")

    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Wyckoff Phase Analysis for {state['symbol']}: {state['technical_data'].get('wyckoff', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class ElliottWaveAgent(BaseAgent):
    def __init__(self):
        super().__init__("ElliottWave")

    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Elliott Wave Theory count for {state['symbol']}: {state['technical_data'].get('waves', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class FundamentalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Fundamental ratios for {state['symbol']}: {state['fundamental_data']}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class EarningsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Earnings")

    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Recent Earnings surprises for {state['symbol']}: {state.get('earnings_data', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class OptionsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Options")

    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Options Chain (PCR, Max Pain, OI) for {state['symbol']}: {state.get('options_data', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class SentimentAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"News sentiment for {state['symbol']}: {state['news_sentiment']}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class MacroAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Global macro indicators: {state.get('macro_data', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class InstitutionalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"FII/DII activity: {state.get('institutional_data', {})}")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class RiskAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = self.get_structured_prompt(f"Multi-Agent Reports for {state['symbol']}: {state['recommendations']}. Assess aggregate risk.")
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class ConsensusAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = f"""
        Final synthesis for {state['symbol']}.
        Reports: {state['recommendations']}

        Provide a final institutional suggestion.
        Format your response as a professional executive summary.
        """
        response = self.llm.invoke(prompt)
        state['consensus'] = response.content
        return state
