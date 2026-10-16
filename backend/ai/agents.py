import math
import json
import time
from typing import Annotated, TypedDict, List, Dict, Any, Optional

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = None

from backend.core.config import settings
from pydantic import BaseModel, Field

class AgentResponse(BaseModel):
    agent_name: str
    signal: str # BUY, SELL, HOLD, UNAVAILABLE
    confidence: float # 0-1
    reasons: List[str]
    risks: List[str]
    supporting_evidence: Dict[str, Any]

class AgentState(TypedDict):
    symbol: str
    regime: str # BULLISH, BEARISH, VOLATILE, SIDEWAYS
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

        if settings.USE_LOCAL_LLM:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.1
            )
            print(f"   [+] {self.name} initialized with Local LLM (Ollama: {settings.OLLAMA_MODEL})")
        elif ChatGroq is not None:
            self.primary_model = "llama-3.3-70b-versatile"
            self.fallback_model = "llama-3.1-8b-instant"

            self.llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=self.primary_model,
                temperature=0.1,
                max_retries=3
            )
        else:
            self.llm = None

    def use_fallback(self):
        if not settings.USE_LOCAL_LLM and ChatGroq is not None and self.llm is not None:
            self.llm.model_name = self.fallback_model

    def call_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        if self.llm is None:
            return None

        retries = 0
        while retries < 2:
            try:
                response = self.llm.invoke(prompt)
                content = response.content

                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    json_str = json_str.replace("'", '"')
                    json_str = re.sub(r',\s*\}', '}', json_str)
                    json_str = re.sub(r',\s*\]', ']', json_str)
                    json_str = re.sub(r'(?<!\\)\n', '\\\\n', json_str)

                    try:
                        data = json.loads(json_str)
                        for key in ['entry', 'target', 'stop_loss', 'conviction']:
                            if key in data:
                                try:
                                    val = str(data[key]).replace('₹', '').replace(',', '').strip()
                                    if val.lower() == 'nan' or val.lower() == 'null':
                                        data[key] = None
                                    else:
                                        data[key] = float(val)
                                except:
                                    data[key] = None
                        return data
                    except:
                        pass

                return None
            except Exception as e:
                if "429" in str(e) and retries == 0:
                    self.use_fallback()
                    retries += 1
                    continue
                else:
                    print(f"   [!] {self.name} Parse Error: {str(e)[:100]}")
                    return None
        return None

class MarketAgent(BaseAgent):
    def __init__(self): super().__init__("MarketAnalyst")
    def analyze(self, state: AgentState):
        prompt = f"""
        Analyze Technical, SMC, Wyckoff, and Elliott Wave data for {state['symbol']}:
        {state['technical_data']}

        Return JSON:
        {{
            "agent_name": "MarketAnalyst",
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "reasons": ["top 3 technical reasons"],
            "risks": ["top 2 risks"],
            "supporting_evidence": {{"wave": "count", "structure": "bias"}}
        }}
        """
        data = self.call_llm(prompt)
        if data: state['recommendations'].append(AgentResponse(**data))
        return state

class CompanyAgent(BaseAgent):
    def __init__(self): super().__init__("CompanyAnalyst")
    def analyze(self, state: AgentState):
        prompt = f"""
        Analyze Fundamentals, Earnings, and Options for {state['symbol']}:
        Fundamentals: {state['fundamental_data']}
        Options: {state['options_data']}

        Return JSON:
        {{
            "agent_name": "CompanyAnalyst",
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "reasons": ["fundamental/options drivers"],
            "risks": ["valuation/liquidity risks"],
            "supporting_evidence": {{"pe": "value", "pcr": "value"}}
        }}
        """
        data = self.call_llm(prompt)
        if data: state['recommendations'].append(AgentResponse(**data))
        return state

class ContextAgent(BaseAgent):
    def __init__(self): super().__init__("ContextAnalyst")
    def analyze(self, state: AgentState):
        prompt = f"""
        Analyze Sentiment, Macro, and Institutional flow for {state['symbol']}:
        Sentiment: {state['news_sentiment']}
        Institutional: {state['institutional_data']}

        Return JSON:
        {{
            "agent_name": "ContextAnalyst",
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.0-1.0,
            "reasons": ["sentiment/context drivers"],
            "risks": ["macro risks"],
            "supporting_evidence": {{"bias": "value"}}
        }}
        """
        data = self.call_llm(prompt)
        if data: state['recommendations'].append(AgentResponse(**data))
        return state

class ConsensusAgent(BaseAgent):
    def __init__(self): super().__init__("ConsensusLead")
    def analyze(self, state: AgentState):
        indicators = state.get('technical_data', {}).get('indicators', {})
        current_price = indicators.get('last_price') or indicators.get('Close') or state.get('last_price', None)
        regime = state.get('regime', 'NEUTRAL')

        entry_val = None
        if current_price is not None and isinstance(current_price, (int, float)) and math.isfinite(current_price) and current_price > 0:
            entry_val = float(current_price)

        def make_unavailable_response(reason_msg: str) -> str:
            return json.dumps({
                "status": "UNAVAILABLE",
                "rating": "UNAVAILABLE",
                "conviction": 0,
                "thesis": reason_msg,
                "entry": entry_val,
                "target": None,
                "stop_loss": None,
                "risk_reward": None,
                "timeframe": "SWING",
                "agent_debate": [],
                "error": "LLM_PROVIDER_UNAVAILABLE"
            })

        if self.llm is None:
            state['consensus'] = make_unavailable_response("LLM provider or dependency unavailable. No trade parameters generated.")
            return state

        template = """
        Final synthesis for {symbol}. CURRENT PRICE: {current_price}
        CURRENT MARKET REGIME: {regime}

        Analyst Reports: {reports}

        INSTRUCTION FOR {regime} REGIME:
        - If BULLISH: Prioritize growth targets and trend following.
        - If VOLATILE: Prioritize capital preservation (tight stops, conservative targets).
        - If SIDEWAYS: Focus on reversal zones and mean reversion.

        Return ONLY a clean JSON object.
        DO NOT return Python code.
        DO NOT explain your reasoning outside the JSON.

        {{
            "rating": "STRONG BUY|BUY|HOLD|SELL|STRONG SELL",
            "timeframe": "INTRADAY|SWING|POSITION|LONG_TERM",
            "conviction": 0 to 100,
            "thesis": "Professional executive summary.",
            "entry": {current_price},
            "target": numeric_price or null,
            "target_range": [min, max],
            "stop_loss": numeric_price or null,
            "stop_range": [min, max],
            "risk_reward": "e.g. 1:2.5",
            "key_catalysts": ["catalyst"],
            "key_risks": ["risk"],
            "invalidation_point": "price level",
            "agent_debate": [
                {{"agent": "MarketAnalyst", "summary": "..."}},
                {{"agent": "CompanyAnalyst", "summary": "..."}},
                {{"agent": "ContextAnalyst", "summary": "..."}}
            ]
        }}
        """

        prompt = template.format(
            symbol=state['symbol'],
            current_price=entry_val if entry_val is not None else "Unknown",
            regime=regime,
            reports=state['recommendations']
        )

        retries = 0
        while retries < 2:
            try:
                response = self.llm.invoke(prompt)
                content = response.content

                import re
                start = content.find('{')
                end = content.rfind('}')
                if start != -1 and end != -1:
                    state['consensus'] = content[start:end+1]
                    return state

                retries += 1
            except Exception as e:
                if "429" in str(e) and retries == 0:
                    self.use_fallback(); retries += 1; continue
                else:
                    state['consensus'] = make_unavailable_response(f"Consensus generation error: {str(e)[:100]}")
                    return state

        state['consensus'] = make_unavailable_response("Failed to generate valid consensus output from LLM.")
        return state
