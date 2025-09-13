import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings

load_dotenv()

class LLMConfig:
    # Manages LLM configurations and model initialization

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key  = os.getenv("ANTHROPIC_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environemnt variables")
        
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environemnt variables")
        

    def get_gpt4(self, temperature = 0.7):
        """
        Returns GPT-4 instance for general reasoning tasks
        Temperature controls creavitity(0 = deterministic, 1 = creative)
        """

        return ChatOpenAI(
            model_name = "gpt-5-mini",
            temperature = temperature,
            openai_api_key=self.openai_api_key
        )
    

    def get_claude(self, temperature = 0.7):
        """
        Returns Claude instance for analysis and verification tasks
        Claude excels at detailed analsysis and fact-checking
        """

        return ChatAnthropic(
            model_name = "claude-sonnet-4-20250514",
            temperature = temperature,
            anthropic_api_key=self.anthropic_api_key
        )
    

    def get_embeddings(self):
        """
        Returns embedding model for converting text to vectors
        Used for semantic search in vector databases
        """
        return OpenAIEmbeddings(openai_api_key=self.openai_api_key)
