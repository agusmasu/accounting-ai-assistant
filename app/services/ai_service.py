import os
import logging
from datetime import datetime
from typing import List, Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from app.services.tools.invoice import create_invoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """
    AI Service that uses a LangGraph ReAct agent with tools to process user inputs
    and create invoices.
    
    Usage example:
    ```python
    # Initialize the service
    ai_service = AIService()
    
    # Process a user request
    response = await ai_service.process_text("Create an invoice for Acme Corp for 5 hours of consulting at $150 per hour")
    
    # Continue the conversation with the same thread ID
    thread_id = response["thread_id"]
    follow_up = await ai_service.continue_conversation("Add a 10% tax to that invoice", thread_id)
    
    # For streaming responses
    async for chunk in ai_service.stream_response("What's the total amount?", thread_id):
        print(chunk)
    ```
    """
    
    def __init__(self):
        # Get OpenAI API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        logger.info(f"OpenAI API Key loaded (first 8 chars): {self.openai_api_key[:8]}...")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=self.openai_api_key
        )
        
        # Set up tools
        self.tools = [create_invoice]
        
        # Initialize memory for conversation persistence
        self.memory = MemorySaver()

        prompt = """
            You are a helpful accountant assistant that can create invoices.
            You can also help with other accounting tasks.
            You can use any of the tools provided to you to help the user.

            Please consider the following rules for creating an invoice:
            - The invoice must be created in the format of the tool provided.
            - If the user decides to not specify a client, you must use the following values:
                - documento_tipo: OTRO
                - documento_nro: 0
                - razon_social: "Sin Especificar"
                - domicilio: "Sin Especificar"
                - provincia: 0    
        """

        # Create the agent
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools, 
            checkpointer=self.memory,
            prompt=prompt,
            debug=False
        )
    
    async def process_text(self, text: str, thread_id: str = None) -> Dict[str, Any]:
        """
        Process text using the agent to extract invoice information and take actions.
        
        Args:
            text: The text input from the user
            thread_id: Unique identifier for the conversation thread (for memory)
            
        Returns:
            The agent's response with extracted information
        """
        # Create a unique thread ID if none provided
        if thread_id is None:
            thread_id = f"thread_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        # Set up configuration with thread ID for memory
        config = {"configurable": {"thread_id": thread_id}}
        
        # Process with the agent
        result = await self.agent_executor.ainvoke(
            {"messages": [HumanMessage(content=text)]},
            config
        )
        
        # Extract the response from the agent result
        processed_result = self._extract_agent_response(result)
        processed_result["thread_id"] = thread_id
        
        return processed_result
    
    async def continue_conversation(self, text: str, thread_id: str) -> Dict[str, Any]:
        """
        Continue an existing conversation with the agent.
        
        Args:
            text: The new text input from the user
            thread_id: The existing conversation thread ID
            
        Returns:
            The agent's response
        """
        # Use the existing thread ID for conversation continuity
        config = {"configurable": {"thread_id": thread_id}}
        
        # Process with the agent
        result = await self.agent_executor.ainvoke(
            {"messages": [HumanMessage(content=text)]}, 
            config
        )
        
        # Extract the response from the agent result
        processed_result = self._extract_agent_response(result)
        processed_result["thread_id"] = thread_id
        
        return processed_result
    
    def _extract_agent_response(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract the AI's response and any tool outputs from the agent result.
        
        Args:
            agent_result: The raw result from the agent executor
            
        Returns:
            Processed result with text response and any tool outputs
        """
        processed_result = {
            "response": "",
            "tool_outputs": [],
            "raw_result": agent_result
        }
        
        # Extract AI message content from messages array
        if "messages" in agent_result:
            messages = agent_result["messages"]
            if messages and len(messages) > 0:
                # Get the last message which is the AI's response
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    processed_result["response"] = last_message.content
        # Fallback for agent property in result
        elif "agent" in agent_result and "messages" in agent_result["agent"]:
            messages = agent_result["agent"]["messages"]
            if messages and len(messages) > 0:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    processed_result["response"] = last_message.content
        
        # Extract tool outputs if available
        if "intermediate_steps" in agent_result:
            for step in agent_result["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) >= 2:
                    # Tool call info is in the first element, result in the second
                    tool_call = step[0]
                    tool_result = step[1]
                    processed_result["tool_outputs"].append({
                        "tool": tool_call.tool if hasattr(tool_call, "tool") else str(tool_call),
                        "input": tool_call.tool_input if hasattr(tool_call, "tool_input") else None,
                        "output": tool_result
                    })
        
        return processed_result 