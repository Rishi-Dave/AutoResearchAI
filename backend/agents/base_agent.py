"""
Base agent class that all specialized agents will inherit from.
Provides common functionality like memory and tool usage
"""

from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any

class BaseAgent:
    """
    Foundation for all AI agents in our system.
    Each agent has:
    - An LLM for reasoning
    - Memory to track conversation
    - Tools to take actions
    - A specific role/purpose
    """

    def __init__(self, llm, tools: List = None, role: str = "Assistant"):
        self.llm = llm
        self.tools = tools or []
        self.role = role
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        #ReAct pattern: Reason + Act

        self.prompt_template = """
        You are a {role}.

        You have access to the following tools:
        {tools}

        Use the following format:
        Thought: Think about what you need to do
        Action: The action to take, should be one of [{tool_names}]
        Action Input: The input to the action
        Observation: The result of the action
        ... repeat (Thought/Action/Action Input/Observation as needed)
        Thought: I now know the final answer
        Final Answer: The answer answer to the original input question

        Previous conversation:
        {chat_history}

        Question: {input}
        {agent_scratchpad}
        """

        self.agent = None
        self._setup_agent()


    def _setup_agent(self):
        """Initialize the agent with LLM and tools"""
        if self.tools:
            prompt = PromptTemplate(
                template = self.prompt_template,
                input_variables = ["input", "chat_history", "agent_scratchpad"],
                partial_variables = {
                    "role": self.role,
                    "tools": "\n".join(f"{t.name}: {t.description}" for t in self.tools),
                    "tool_names": ", ".join([t.name for t in self.tools])
                }   
            )


        
            agent = create_react_agent(
                llm = self.llm,
                tools = self.tools,
                prompt = prompt
            )

            self.agent = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory = self.memory,
                verbose=True,
                handle_parsing_errors = True
            )

    def run(self, input_text: str) -> str:
        """Execute the agent with given input """
        if self.agent:
            try:
                response = self.agent.invoke({"input": input_text})
                # Check for the correct output key
                return response.get("output", "No output found")
            except Exception as e:
                # Handle cases where the agent doesn't produce an output
                return f"An error occurred during agent execution: {e}"
        else:
            #no tool = not an agent, so just use LLM
            return self.llm.predict(input_text)
        
    def clear_memory(self):
        """Reset conversation memory"""
        self.memory.clear()
