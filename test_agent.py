# A simple test script for base_agent.py
import os
from langchain.tools import Tool
from backend.agents.base_agent import BaseAgent
from backend.config.llm_config import LLMConfig



def test_llm_config():
    print("Testing LLMConfig...")
    try:
        llm_config = LLMConfig()
        print("LLMConfig initialized successfully.")

        # Test getting GPT-4 instance
        gpt4 = llm_config.get_gpt4()
        print(f"Retrieved GPT-4 instance: {gpt4}")

        # Test getting Claude instance
        claude = llm_config.get_claude()
        print(f"Retrieved Claude instance: {claude}")

        # Test getting embeddings model
        embeddings = llm_config.get_embeddings()
        print(f"Retrieved embeddings model: {embeddings}")

        # A simple, quick test to see if the LLM works
        print("\nTesting LLM prediction...")
        response = gpt4.predict("Say hello, world!")
        print(f"LLM response: {response}")

        print("\nTesting LLM prediction...")
        response = claude.predict("Say bye now!")
        print(f"LLM response: {response}")

        print("\nAll LLM connections appear to be working!")

    except ValueError as e:
        print(f"Failed to initialize LLMConfig: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def dummy_tool(text: str) -> str:
    """A simple tool that just returns the input."""
    return f"Tool was called with input: {text}"

def test_base_agent():
    print("\nTesting BaseAgent...")
    llm_config = LLMConfig()
    llm_instance = llm_config.get_gpt4()
    
    # Case 1: Test with no tools
    print("\n--- Testing agent without tools ---")
    no_tool_agent = BaseAgent(llm=llm_instance, role="Simple Assistant")
    try:
        response = no_tool_agent.run("What is the capital of France?")
        print(f"No-tool agent response: {response}")
    except Exception as e:
        print(f"No-tool agent failed: {e}")

    # Case 2: Test with tools
    print("\n--- Testing agent with a dummy tool ---")
    tools = [
        Tool(
            name="dummy_tool",
            func=dummy_tool,
            description="A dummy tool that echoes its input."
        )
    ]
    tool_agent = BaseAgent(llm=llm_instance, tools=tools, role="Tool-using Assistant")
    try:
        # The agent should use the tool here
        response = tool_agent.run("Action: dummy_tool\nAction Input: Test Input")
        print(f"Tool-using agent response: {response}")
    except Exception as e:
        print(f"Tool-using agent failed: {e}")

    # Test clearing memory
    print("\n--- Testing memory clear ---")
    tool_agent.clear_memory()
    print("Agent memory cleared.")

if __name__ == "__main__":
    test_llm_config() # Run the LLM test first
    test_base_agent()