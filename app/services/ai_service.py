import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from ..models.invoice import Invoice, InvoiceItem
import speech_recognition as sr
from pydub import AudioSegment
import io

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
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
        
        # Create prompt for invoice extraction
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that extracts invoice information from voice messages.
            Extract the following information:
            - Customer name
            - Customer tax ID
            - Customer address
            - Items (description, quantity, unit price)
            - Payment method
            
            Format the response as a JSON object matching the Invoice model."""),
            ("user", "{text}")
        ])
        
        # Process with LLM
        chain = prompt | self.llm | self.parser
        invoice = await chain.ainvoke({"text": text})
        
        return invoice.dict()
    
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