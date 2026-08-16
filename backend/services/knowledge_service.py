import os
from typing import List, Dict, Any, Optional
from backend.domain.interfaces.repository import IDataPlatformRepository

class KnowledgeService:
    def __init__(self, repository: IDataPlatformRepository, model_name: str = 'all-MiniLM-L6-v2'):
        self.repository = repository
        self.model_name = model_name
        self.doc_map: List[Dict[str, Any]] = []
        # Free Tier Optimization: Local semantic search disabled to stay under 512MB RAM
        # In enterprise mode, use FAISS + SentenceTransformers

    def index_document(self, text: str, metadata: Dict[str, Any]):
        """
        Lightweight indexer using simple document storage.
        """
        self.doc_map.append({"text": text, "metadata": metadata})

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simplified keyword-based search for free-tier cloud environments.
        """
        query = query.lower()
        results = []
        for doc in self.doc_map:
            if query in doc["text"].lower() or any(query in str(v).lower() for v in doc["metadata"].values()):
                results.append(doc)
            if len(results) >= top_k:
                break
        return results

    def save_index(self):
        # Local state persistence can be added if needed via JSON
        pass

    def load_index(self):
        pass
