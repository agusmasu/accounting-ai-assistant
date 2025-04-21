import asyncio
from app.services.ai import AIService
from app.services.tusfacturas import TusFacturasService
from app.services.memory import MemoryService
from app.models.invoice import InvoiceInputData
import json
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

async def main():
    # Initialize services
    memory_service = MemoryService()
    ai_service = AIService(memory_service=memory_service)
    tusfacturas_service = TusFacturasService()
    
    # Create a unique thread ID for this conversation session
    session_thread_id = f"console_chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print("Welcome to FacturAI Console Chat!")
    print("You can describe an invoice and I'll help you generate it.")
    print("Type 'exit' to quit.")
    print("Type 'new session' to start a new conversation thread.")
    print("\nExample input:")
    print("Generate an invoice for Juan Pérez with CUIT 30-71234567-8, address Av. Corrientes 1234, for 2 hours of consulting at $5000 per hour")
    print("\n--- Starting new conversation thread ---")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                break
            
            if user_input.lower() == 'new session':
                session_thread_id = f"console_chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                print("\n--- Starting new conversation thread ---")
                continue
                
            if not user_input:
                continue
                
            # Process with AI using the persistent thread ID
            print("\nAI is thinking...")
            result = await ai_service.process_text(user_input, session_thread_id)
            
            # Extract response and invoice data from result
            response = result.get("response", "")
            tool_outputs = result.get("tool_outputs", [])
            
            # Print AI response in a clean format
            print(f"\nAI: {response}")
            
            # Check if invoice data is available from tool output
            invoice_data = None
            for tool_output in tool_outputs:
                if "create_invoice" in str(tool_output.get("tool", "")):
                    invoice_data = tool_output.get("output")
                    break
                    
            # If invoice data was extracted, ask the user if they want to create it
            if invoice_data:
                print("\nDetected invoice data:")
                print(json.dumps(invoice_data, indent=2, ensure_ascii=False))
                
                create_choice = input("\nDo you want to create this invoice? (yes/no): ").strip().lower()
                
                if create_choice == 'yes' or create_choice == 'y':
                    print("\nCreating invoice with TusFacturas...")
                    try:
                        invoice_result = tusfacturas_service.create_invoice(invoice_data)
                        print(f"Success! Invoice created: {invoice_result}")
                    except Exception as e:
                        print(f"Error creating invoice: {str(e)}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 