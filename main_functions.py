import asyncio
import logging
from app.services.ai import AIService
from app.services.memory import MemoryService
import flask
import functions_framework
from langchain_core.messages import HumanMessage
import json

memory_service = MemoryService()
ai_service = AIService(memory_service=memory_service)
logger = logging.getLogger(__name__)

@functions_framework.http
def send_message(request: flask.Request) -> flask.typing.ResponseReturnValue:
    # Get the message from the req body
    message = request.json.get('message')
    
    if not message:
        print("No message provided")
        return flask.jsonify({"error": "Message is required"}), 400
    
    print(f"Processing message: {message}")
    response = asyncio.run(ai_service.process_text(message))
    
    logger.info(f"Response: {response}")

    # Print the structure of the response object
    print(f"Response structure: {response}")

    # Extract only the directly serializable parts of the response
    serializable_response = {
        "response": response.get("response", ""),
        "thread_id": response.get("thread_id", "")
    }
    
    return flask.jsonify(serializable_response)
