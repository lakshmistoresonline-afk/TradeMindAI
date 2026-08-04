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
        prompt = f"Analyze these technical indicators for {state['symbol']}: {state['technical_data']}"
        response = self.llm.invoke(prompt)
        state['recommendations'].append({"agent": "Technical", "analysis": response})
        return state

class FundamentalAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = f"Analyze these fundamental ratios for {state['symbol']}: {state['fundamental_data']}"
        response = self.llm.invoke(prompt)
        state['recommendations'].append({"agent": "Fundamental", "analysis": response})
        return state

class ConsensusAgent(BaseAgent):
    def analyze(self, state: AgentState):
        prompt = f"Given these reports: {state['recommendations']}, provide a final consensus for {state['symbol']}."
        response = self.llm.invoke(prompt)
        state['consensus'] = response
        return state
