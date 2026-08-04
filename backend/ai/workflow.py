from langgraph.graph import StateGraph, END
from backend.ai.agents import AgentState, TechnicalAgent, FundamentalAgent, SentimentAgent, ConsensusAgent

def create_ai_workflow():
    workflow = StateGraph(AgentState)

    tech_agent = TechnicalAgent("Technical")
    fund_agent = FundamentalAgent("Fundamental")
    sent_agent = SentimentAgent("Sentiment")
    consensus_agent = ConsensusAgent("Consensus")

    workflow.add_node("technical_analysis", tech_agent.analyze)
    workflow.add_node("fundamental_analysis", fund_agent.analyze)
    workflow.add_node("sentiment_analysis", sent_agent.analyze)
    workflow.add_node("consensus", consensus_agent.analyze)

    workflow.set_entry_point("technical_analysis")
    workflow.add_edge("technical_analysis", "fundamental_analysis")
    workflow.add_edge("fundamental_analysis", "sentiment_analysis")
    workflow.add_edge("sentiment_analysis", "consensus")
    workflow.add_edge("consensus", END)

    return workflow.compile()
