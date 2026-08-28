from backend.ai.agents import AgentState

def create_ai_workflow():
    """
    Consolidated Institutional AI Workflow for Rate Limit Efficiency.
    """
    from langgraph.graph import StateGraph, END
    from backend.ai.agents import (
        MarketAgent, CompanyAgent, ContextAgent, ConsensusAgent
    )

    workflow = StateGraph(AgentState)

    # Initialize Agents
    market = MarketAgent()
    company = CompanyAgent()
    context = ContextAgent()
    consensus = ConsensusAgent()

    # Add Nodes
    workflow.add_node("market", market.analyze)
    workflow.add_node("company", company.analyze)
    workflow.add_node("context", context.analyze)
    workflow.add_node("consensus", consensus.analyze)

    # Define Execution Flow
    workflow.set_entry_point("market")

    workflow.add_edge("market", "company")
    workflow.add_edge("company", "context")
    workflow.add_edge("context", "consensus")
    workflow.add_edge("consensus", END)

    return workflow.compile()
