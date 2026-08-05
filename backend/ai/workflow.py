from langgraph.graph import StateGraph, END
from backend.ai.agents import AgentState, TechnicalAgent, FundamentalAgent, SentimentAgent, RiskAgent, ConsensusAgent, MacroAgent, InstitutionalAgent

def create_ai_workflow():
    workflow = StateGraph(AgentState)

    tech_agent = TechnicalAgent("Technical")
    fund_agent = FundamentalAgent("Fundamental")
    sent_agent = SentimentAgent("Sentiment")
    macro_agent = MacroAgent("Macro")
    inst_agent = InstitutionalAgent("Institutional")
    risk_agent = RiskAgent("Risk")
    consensus_agent = ConsensusAgent("Consensus")

    workflow.add_node("technical_analysis", tech_agent.analyze)
    workflow.add_node("fundamental_analysis", fund_agent.analyze)
    workflow.add_node("sentiment_analysis", sent_agent.analyze)
    workflow.add_node("macro_analysis", macro_agent.analyze)
    workflow.add_node("institutional_analysis", inst_agent.analyze)
    workflow.add_node("risk_analysis", risk_agent.analyze)
    workflow.add_node("consensus", consensus_agent.analyze)

    workflow.set_entry_point("technical_analysis")
    workflow.add_edge("technical_analysis", "fundamental_analysis")
    workflow.add_edge("fundamental_analysis", "sentiment_analysis")
    workflow.add_edge("sentiment_analysis", "macro_analysis")
    workflow.add_edge("macro_analysis", "institutional_analysis")
    workflow.add_edge("institutional_analysis", "risk_analysis")
    workflow.add_edge("risk_analysis", "consensus")
    workflow.add_edge("consensus", END)

    return workflow.compile()
