from typing import Dict, Any
from backend.domain.interfaces.ai_provider import IAIProvider
from backend.ai.workflow import create_ai_workflow
from langchain_groq import ChatGroq
from backend.core.config import settings

class GroqAIProvider(IAIProvider):
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192",
            temperature=0.1
        )
        self.workflow = create_ai_workflow()

    async def generate_analysis(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)
        return response.content

    async def invoke_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self.workflow.ainvoke(state)
