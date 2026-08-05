import faiss
import numpy as np
import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from backend.domain.interfaces.repository import IDataPlatformRepository

class KnowledgeService:
    def __init__(self, repository: IDataPlatformRepository, model_name: str = 'all-MiniLM-L6-v2'):
        self.repository = repository
        self.model = SentenceTransformer(model_name)
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.doc_map: List[Dict[str, Any]] = []
        self.index_path = "backend/data/vector_store.index"

    def index_document(self, text: str, metadata: Dict[str, Any]):
        """
        Embeds and indexes a document chunk.
        """
        embedding = self.model.encode([text])[0]
        self.index.add(np.array([embedding]).astype('float32'))
        self.doc_map.append({"text": text, "metadata": metadata})

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic search across indexed knowledge.
        """
        query_embedding = self.model.encode([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.doc_map):
                results.append(self.doc_map[idx])
        return results

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        # In enterprise, we'd save doc_map to Firestore or as a sidecar file

    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
