from langgraph.graph import StateGraph, END
from backend.ai.agents import (
    AgentState, TechnicalAgent, ICTAgent, WyckoffAgent, ElliottWaveAgent,
    FundamentalAgent, EarningsAgent, OptionsAgent, SentimentAgent,
    MacroAgent, InstitutionalAgent, RiskAgent, ConsensusAgent
)

def create_ai_workflow():
    workflow = StateGraph(AgentState)

    # Initialize Agents
    tech = TechnicalAgent("Technical")
    ict = ICTAgent()
    wyckoff = WyckoffAgent()
    waves = ElliottWaveAgent()
    fund = FundamentalAgent("Fundamental")
    earnings = EarningsAgent()
    options = OptionsAgent()
    sent = SentimentAgent("Sentiment")
    macro = MacroAgent("Macro")
    inst = InstitutionalAgent("Institutional")
    risk = RiskAgent("Risk")
    consensus = ConsensusAgent("Consensus")

    # Add Nodes
    workflow.add_node("technical", tech.analyze)
    workflow.add_node("ict", ict.analyze)
    workflow.add_node("wyckoff", wyckoff.analyze)
    workflow.add_node("waves", waves.analyze)
    workflow.add_node("fundamental", fund.analyze)
    workflow.add_node("earnings", earnings.analyze)
    workflow.add_node("options", options.analyze)
    workflow.add_node("sentiment", sent.analyze)
    workflow.add_node("macro", macro.analyze)
    workflow.add_node("institutional", inst.analyze)
    workflow.add_node("risk", risk.analyze)
    workflow.add_node("consensus", consensus.analyze)

    # Define Execution Flow (Parallel tracks where possible in future, sequential for now)
    workflow.set_entry_point("technical")

    workflow.add_edge("technical", "ict")
    workflow.add_edge("ict", "wyckoff")
    workflow.add_edge("wyckoff", "waves")
    workflow.add_edge("waves", "fundamental")
    workflow.add_edge("fundamental", "earnings")
    workflow.add_edge("earnings", "options")
    workflow.add_edge("options", "sentiment")
    workflow.add_edge("sentiment", "macro")
    workflow.add_edge("macro", "institutional")
    workflow.add_edge("institutional", "risk")
    workflow.add_edge("risk", "consensus")
    workflow.add_edge("consensus", END)

    return workflow.compile()
