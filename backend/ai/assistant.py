from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

class AIChatAssistant:
    def __init__(self):
        self.llm = Ollama(model="llama3")
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory
        )

    def ask(self, query: str):
        return self.conversation.predict(input=query)
