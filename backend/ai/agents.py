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

        # Using Llama 3.1 8B for high-throughput batch processing
        # Integrated with Retry logic for Rate Limit Resilience
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.1,
            max_retries=3 # Built-in langchain retry
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
        prompt = self.get_structured_prompt(f"""
        Assess aggregate risk for {state['symbol']}.
        Technical Data: {state['technical_data']}
        Analyst Reports: {state['recommendations']}

        Focus on:
        - Divergence between Price and Volume.
        - Counter-trend institutional flows.
        - Extreme valuation levels.
        - Upcoming event risk (Earnings/Budget).
        """)
        response = self.llm.invoke(prompt)
        try:
            import json
            state['recommendations'].append(AgentResponse(**json.loads(response.content)))
        except: pass
        return state

class ConsensusAgent(BaseAgent):
    def analyze(self, state: AgentState):
        current_price = state.get('technical_data', {}).get('indicators', {}).get('last_price', 'Unknown')

        prompt = f"""
        Final synthesis for {state['symbol']}.
        CURRENT PRICE: {current_price}

        Institutional Priority Weighting:
        1. Technical & SMC: 40% (Foundation)
        2. Macro & Institutional: 25% (Market Context)
        3. Fundamental: 20% (Long-term value)
        4. Sentiment & Options: 15% (Short-term noise)

        Analyst Reports: {state['recommendations']}

        Synthesize these reports into a final institutional decision.
        If agents conflict, prioritize the Technical/SMC bias unless Macro risk is EXTREME.

        Return ONLY a structured JSON response. DO NOT explain. DO NOT use markdown code blocks.
        IMPORTANT: 'target', 'stop_loss', and 'entry' MUST be numeric floats. DO NOT include currency symbols or units.
        IMPORTANT: 'timeframe' MUST be one of: "INTRADAY", "SWING", "MID_TERM", "LONG_TERM".

        {{
            "rating": "BUY | SELL | HOLD | STRONG BUY | STRONG SELL",
            "timeframe": "INTRADAY | SWING | MID_TERM | LONG_TERM",
            "conviction": 0 to 100,
            "thesis": "Complete professional summary of why this decision was made.",
            "entry": numeric_entry_price,
            "target": numeric_price_target,
            "stop_loss": numeric_stop_loss,
            "risk_reward": "e.g. 1:2.5",
            "key_catalysts": ["catalyst 1", "catalyst 2"],
            "key_risks": ["risk 1", "risk 2"],
            "invalidation_point": "specific price or event"
        }}
        """
        response = self.llm.invoke(prompt)
        state['consensus'] = response.content
        return state
