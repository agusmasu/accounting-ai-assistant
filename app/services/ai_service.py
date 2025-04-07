import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from ..models.invoice import Invoice, InvoiceItem
import speech_recognition as sr
from pydub import AudioSegment
import io
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        logger.info(f"OpenAI API Key loaded (first 8 chars): {self.openai_api_key[:8]}...")
        
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            openai_api_key=self.openai_api_key
        )
        self.parser = PydanticOutputParser(pydantic_object=Invoice)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
    async def process_voice(self, voice_data: bytes) -> dict:
        """Process voice message and extract invoice information"""
        # Convert voice data to text
        text = await self._speech_to_text(voice_data)
        return await self.process_text(text)
        
    async def process_text(self, text: str) -> dict:
        """Process text and extract invoice information"""
        # Create prompt for invoice extraction
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = ChatPromptTemplate.from_template(
            """You are an AI assistant that extracts invoice information from text.
            Extract the following information from this text: {input_text}
            
            You MUST extract or provide default values for ALL of the following information:
            - Customer name (REQUIRED): The full name or company name of the customer
            - Customer tax ID (REQUIRED): A valid CUIT number in format XX-XXXXXXXX-X
            - Customer address (REQUIRED): The complete address of the customer
            - Items (REQUIRED): At least one item with description, quantity, and unit price
            - Payment method (REQUIRED): One of: "Transfer", "Cash", "Credit Card", "Debit Card"
            
            If any required information is missing from the input text, provide sensible defaults:
            - For customer name: Use "Cliente Consumidor Final" if not specified
            - For tax ID: Use "20-00000000-0" (Consumidor Final) if not specified
            - For address: Use "Av. Corrientes 1234, CABA" if not specified
            - For payment method: Use "Transfer" if not specified
            
            Format the response as a JSON object matching this schema:
            {{
                "customer_name": "string",
                "customer_tax_id": "string (CUIT format: XX-XXXXXXXX-X)",
                "customer_address": "string",
                "items": [{{
                    "description": "string",
                    "quantity": number,
                    "unit_price": number,
                    "tax_rate": 0.21
                }}],
                "invoice_date": "{current_date}",
                "invoice_type": "C",  # Use "C" for Consumidor Final
                "payment_method": "string",
                "currency": "ARS"
            }}"""
        )
        
        # Process with LLM
        chain = prompt | self.llm | self.parser
        result = await chain.ainvoke({"input_text": text, "current_date": current_date})
        return result
    
    async def _speech_to_text(self, voice_data: bytes) -> str:
        """Convert voice data to text using speech recognition"""
        # Convert voice data to WAV format
        audio = AudioSegment.from_file(io.BytesIO(voice_data))
        wav_data = io.BytesIO()
        audio.export(wav_data, format="wav")
        wav_data.seek(0)
        
        # Use speech recognition
        with sr.AudioFile(wav_data) as source:
            audio_data = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio_data, language="es-AR")
                return text
            except sr.UnknownValueError:
                raise Exception("Could not understand audio")
            except sr.RequestError:
                raise Exception("Could not request results from speech recognition service") 