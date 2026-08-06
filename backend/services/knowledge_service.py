import numpy as np
import os
from typing import List, Dict, Any, Optional
from backend.domain.interfaces.repository import IDataPlatformRepository

class KnowledgeService:
    def __init__(self, repository: IDataPlatformRepository, model_name: str = 'all-MiniLM-L6-v2'):
        self.repository = repository
        self.model_name = model_name
        self._model = None
        self._index = None
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        self.doc_map: List[Dict[str, Any]] = []
        self.index_path = "backend/data/vector_store.index"

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def index(self):
        if self._index is None:
            import faiss
            self._index = faiss.IndexFlatL2(self.dimension)
        return self._index

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
        import faiss
        faiss.write_index(self.index, self.index_path)
        # In enterprise, we'd save doc_map to Firestore or as a sidecar file

    def load_index(self):
        if os.path.exists(self.index_path):
            import faiss
            self._index = faiss.read_index(self.index_path)
