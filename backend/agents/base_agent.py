from abc import ABC, abstractmethod
import os

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema import HumanMessage
from dotenv import load_dotenv

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

        load_dotenv()
        
        # Check if we should use Ollama
        use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if use_ollama:
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.llm = Ollama(model="qwen2.5:latest", base_url=ollama_url)
        else:
            self.llm = ChatOpenAI(model="o4-mini")

    @abstractmethod
    def run(self, input: str) -> str:
        pass

    def invoke(self, input: str) -> str:
        return self.llm.invoke(input)
