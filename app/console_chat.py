import asyncio
from app.services.ai_service import AIService
from app.services.tusfacturas_service import TusFacturasService
from app.models.invoice import Invoice
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

async def main():
    # Initialize services
    ai_service = AIService()
    tusfacturas_service = TusFacturasService()
    
    print("Welcome to FacturAI Console Chat!")
    print("You can describe an invoice and I'll help you generate it.")
    print("Type 'exit' to quit.")
    print("\nExample input:")
    print("Generate an invoice for Juan Pérez with CUIT 30-71234567-8, address Av. Corrientes 1234, for 2 hours of consulting at $5000 per hour")
    
    while True:
        try:
            # Get user input
            user_input = input("\nDescribe the invoice: ").strip()
            
            if user_input.lower() == 'exit':
                break
                
            if not user_input:
                continue
                
            # Process with AI
            print("\nProcessing your request...")
            invoice_data = await ai_service.process_text(user_input)
            
            # Print extracted information
            print("\nExtracted Invoice Information:")
            print(json.dumps(invoice_data.dict(), indent=2, default=str))
            
            # Ask for confirmation
            confirm = input("\nWould you like to generate this invoice? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                print("\nGenerating invoice...")
                invoice_response = await tusfacturas_service.generate_invoice(invoice_data)
                print("\nInvoice generated successfully!")
                print(f"Invoice number: {invoice_response['invoice_number']}")
                print(f"PDF URL: {invoice_response['pdf_url']}")
            else:
                print("\nInvoice generation cancelled.")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with a different input.")

if __name__ == "__main__":
    asyncio.run(main()) 