import base64
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydub import AudioSegment
import io
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from app.models.user import User
from app.services.conversation import ConversationService
from app.services.memory import MemoryService
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.context import ContextService

from app.services.tools.invoice import create_invoice
from app.services.tusfacturas import TusFacturasService
from app.services.user import UserService
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """
    AI Service that uses a LangGraph ReAct agent with tools to process user inputs
    and create invoices.
    """
    
    def __init__(self, memory_service: MemoryService = None, conversation_service: ConversationService = None, user_service: UserService = None):
        # Get OpenAI API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.user_service = user_service
        self.conversation_service = conversation_service
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        logger.info(f"OpenAI API Key loaded (first 8 chars): {self.openai_api_key[:8]}...")
        
        # Initialize Memory Service if not provided
        self.memory_service = memory_service
        logger.info("Memory Service injected into AIService")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=self.openai_api_key
        )

        self.openai_client = OpenAI(
            api_key=self.openai_api_key
        )

        self.voice_llm = ChatOpenAI(
            model="gpt-4o-mini-transcribe",
            openai_api_key=self.openai_api_key,
            temperature=0
        )

        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash",
        #     google_api_key=self.gemini_api_key,
        #     temperature=0
        # )

        # Set up tools

        tusfacturas_service = TusFacturasService(self.user_service)
        self.tools = [create_invoice]
        # self.tools = [create_invoice_test]
        
        # Initialize memory for conversation persistence
        self.memory = self.memory_service.get_checkpointer()
        logger.info("Using PostgreSQL checkpointer from MemoryService")

        prompt = """
            You are a helpful accountant assistant specialized in creating invoices and managing accounting tasks.

            ## Your Role
            - You help users create invoices and answer accounting questions
            - You communicate exclusively through WhatsApp
            - You provide concise, direct responses (max 3-4 sentences per message)
            - You break complex information into multiple short messages when needed

            ## Invoice Creation Rules
            When creating an invoice:
            - Follow exactly the format required by the tool
            - For unspecified clients, use these default values:
                - documento_tipo: OTRO
                - documento_nro: 0
                - razon_social: "Sin Especificar"
                - domicilio: "Sin Especificar"
                - provincia: 0

            ## Communication Style
            - Keep messages brief and to the point
            - Use simple language
            - Ask clarifying questions when information is missing
            - Confirm actions before executing them
            - Avoid lengthy explanations
        
            ## User Information
            - The user's name is {user_name}
            - The user's phone number is {user_phone_number}
            - The user's email is {user_email}
        
        """

        # Create the agent
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools, 
            checkpointer=self.memory,
            prompt=prompt,
            debug=True
        )
    
    async def process_text(self, text: str, from_phone_number: str) -> Dict[str, Any]:
        """
        Process text using the agent to extract invoice information and take actions.
        
        Args:
            text: The text input from the user
            from_phone_number: The phone number of the sender (for user lookup)
            
        Returns:
            The agent's response with extracted information
        """
        # Get the user from context
        user = ContextService.get_current_user()
        if not user:
            logger.error("No user found in context")
            raise ValueError("User not found in context")
            
        # Get the current conversation
        conversation = self.conversation_service.get_current_conversation(user.id)

        # Set up configuration with thread ID for memory
        config = {"configurable": {"thread_id": conversation.thread_id}}

        # Process with the agent
        result = self.agent_executor.invoke(
            {
                "messages": [HumanMessage(content=text)],
                "user_name": user.name,
                "user_phone_number": user.phone_number,
                "user_email": user.email
            },
            config
        )
        
        # Extract the response from the agent result
        processed_result = self._extract_agent_response(result)
        processed_result["thread_id"] = conversation.thread_id

        # Update the last message at for the conversation
        self.conversation_service.update_last_message_at(conversation.id)

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
    
    async def process_voice(self, voice: bytes, content_type: str, sender_phone: str) -> Dict[str, Any]:
        """
        Process voice using the agent to extract invoice information and take actions.
        
        Args:
            voice: The voice message data
            content_type: The content type of the voice message
            sender_phone: The phone number of the sender (used for user lookup)
        """
        # Convert audio to mp3 format using pydub
        logger.info(f"Converting audio file from {content_type} to mp3")
        
        file_type = content_type.split('/')[-1]
        logger.info(f"Received a file type: {file_type}")

        # Load audio from bytes into pydub
        audio = AudioSegment.from_file(io.BytesIO(voice), format=file_type)
        
        # Export as mp3 to bytes buffer
        mp3_buffer = io.BytesIO()
        audio.export(mp3_buffer, format="mp3")
        mp3_buffer.seek(0)
        voice = mp3_buffer.read()

        logger.info(f"Audio successfully converted to mp3 format")
        
        # Create a file-like object with a name attribute for the OpenAI API
        mp3_file = io.BytesIO(voice)
        mp3_file.name = "audio.mp3"  # The name with extension is important

        transcription = self.openai_client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", 
            file=mp3_file
        )

        text = transcription.text
        logger.info("Processing text response with the text agent")

        return await self.process_text(text=text, from_phone_number=sender_phone)
