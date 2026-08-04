from typing import Annotated, TypedDict, List
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    symbol: str
    technical_data: dict
    fundamental_data: dict
    news_sentiment: dict
    recommendations: List[dict]
    consensus: str

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = Ollama(model="llama3") # Default to llama3 via Ollama

class TechnicalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        # Implementation of technical analysis logic using LLM
        smc_data = state.get('technical_data', {}).get('smc', {})
        indicators = state.get('technical_data', {}).get('indicators', {})

        prompt = f"""
        Analyze these technical indicators and Smart Money Concepts for {state['symbol']}:

        Indicators: {indicators}
        SMC Data (Order Blocks & FVG): {smc_data}

        Provide a detailed technical outlook. Focus on trend, momentum, and potential institutional liquidity zones.
        """
        response = self.llm.invoke(prompt)
        state['recommendations'].append({"agent": "Technical", "analysis": response})
        return state

class FundamentalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = f"""
        Analyze these fundamental ratios for {state['symbol']}: {state['fundamental_data']}

        Provide an assessment of the company's valuation and financial health.
        """
        response = self.llm.invoke(prompt)
        state['recommendations'].append({"agent": "Fundamental", "analysis": response})
        return state

class SentimentAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)

    def analyze(self, state: AgentState):
        sentiment = state.get('news_sentiment', {})
        prompt = f"Analyze the following market sentiment data for {state['symbol']}: {sentiment}. How does the news impact the short-term outlook?"
        response = self.llm.invoke(prompt)
        state['recommendations'].append({"agent": "Sentiment", "analysis": response})
        return state

class ConsensusAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = f"Given these reports: {state['recommendations']}, provide a final consensus for {state['symbol']}."
        response = self.llm.invoke(prompt)
        state['consensus'] = response
        return state
