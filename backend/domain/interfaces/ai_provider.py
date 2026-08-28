from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IAIProvider(ABC):
    @abstractmethod
    async def generate_analysis(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def invoke_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass
