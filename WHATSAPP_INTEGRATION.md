# FacturAI WhatsApp Integration

This document provides instructions on how to set up and test the WhatsApp integration for FacturAI.

## Prerequisites

- Python 3.8+
- ngrok installed and configured
- WhatsApp Business API account
- OpenAI API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

## Running the Integration

1. Run the integration script:

```bash
./run_with_ngrok.py
```

2. The script will:
   - Start the FastAPI server
   - Start ngrok and expose your local server
   - Display the webhook URL and verify token

3. Use the displayed webhook URL and verify token to configure your WhatsApp webhook.

## Configuring WhatsApp Webhook

1. Go to your WhatsApp Business API dashboard
2. Navigate to the webhook configuration section
3. Add the webhook URL displayed by the script
4. Set the verify token to the one displayed by the script
5. Save the configuration

## Testing the Integration

1. Send a message to your WhatsApp number
2. The message will be processed by the AI agent
3. The AI agent's response will be sent back to your WhatsApp

## Testing Without WhatsApp

You can test the integration without actually sending messages to WhatsApp using the provided test script:

```bash
# Test sending a text message
./test_whatsapp_integration.py --url https://your-ngrok-url.ngrok.io --message "Create an invoice for Acme Corp"

# Test sending an image message
./test_whatsapp_integration.py --url https://your-ngrok-url.ngrok.io --type image

# Test webhook verification
./test_whatsapp_integration.py --url https://your-ngrok-url.ngrok.io --type verify
```

Replace `https://your-ngrok-url.ngrok.io` with the actual ngrok URL displayed by the `run_with_ngrok.py` script.

## Troubleshooting

- If ngrok fails to start, make sure it's installed and configured correctly
- If the webhook verification fails, check that the verify token matches
- If messages aren't being processed, check the server logs for errors

## Security Considerations

- The verify token should be kept secret
- The WhatsApp token should be kept secret
- The OpenAI API key should be kept secret
- The ngrok URL will change each time you restart the script 