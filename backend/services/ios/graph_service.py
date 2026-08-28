from typing import List, Dict, Any
from backend.domain.interfaces.repository import IStockRepository

class KnowledgeGraphService:
    def __init__(self, repository: IStockRepository):
        self.repository = repository

    async def get_stock_relations(self, symbol: str) -> Dict[str, Any]:
        """
        Builds a semantic relationship graph for a stock.
        """
        stock = await self.repository.get_stock_by_symbol(symbol)
        if not stock: return {"nodes": [], "edges": []}

        # In a full enterprise app, we'd use a graph DB like Neo4j.
        # For free-tier, we build it semantically from Firestore metadata.

        # 1. Competitors (Same Sector & Industry)
        all_stocks = await self.repository.get_all_stocks(limit=100)
        peers = [s for s in all_stocks if s.sector == stock.sector and s.symbol != symbol]

        nodes = [{"id": symbol, "label": symbol, "type": "PRIMARY"}]
        edges = []

        # Add Peers
        for peer in peers[:5]: # Top 5 peers
            nodes.append({"id": peer.symbol, "label": peer.symbol, "type": "COMPETITOR"})
            edges.append({"from": symbol, "to": peer.symbol, "label": "PEER"})

        # Add Sector
        sector_id = f"sector_{stock.sector}"
        nodes.append({"id": sector_id, "label": stock.sector, "type": "SECTOR"})
        edges.append({"from": symbol, "to": sector_id, "label": "MEMBER_OF"})

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "sector": stock.sector,
                "industry": stock.industry,
                "peer_count": len(peers)
            }
        }
