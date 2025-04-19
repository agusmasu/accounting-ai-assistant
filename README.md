# FacturAI - Voice-Controlled Invoice Generator

A WhatsApp bot that generates invoices using voice commands. The application uses AI to process voice messages and create invoices automatically through TusFacturasApp.

## Features

- Voice message processing through WhatsApp
- AI-powered invoice generation
- TusFacturasApp integration
- Secure authentication and authorization

## Prerequisites

- Python 3.8+
- WhatsApp Business API account
- TusFacturasApp account with API access
- OpenAI API key for voice processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/facturai.git
cd facturai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```env
# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_VERIFY_TOKEN=your_verify_token

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# TusFacturasApp Configuration
TUSFACTURAS_USER_TOKEN=your_tusfacturas_user_token
TUSFACTURAS_API_TOKEN=your_tusfacturas_api_token
TUSFACTURAS_API_KEY=your_tusfacturas_api_key
```

## Usage

### Running the FastAPI Server

Start the application with Uvicorn:
```bash
uvicorn app.main:app --reload
```

This runs the server at http://localhost:8000

### Running the Console Chat Interface

Run the interactive console chat interface:
```bash
python -m app.console_chat
```

This provides a terminal-based interface to interact with the AI assistant.

### Running in Google Cloud Functions Emulator

Run the application using the Functions Framework emulator:
```bash
functions-framework --target=http_function --source=main_functions.py --debug
```

This runs the server at http://localhost:8080

### API Endpoints

1. Configure your WhatsApp webhook to point to your server's `/webhook/whatsapp` endpoint.

2. Send a voice message to your WhatsApp number with the invoice details.

3. The bot will:
   - Process the voice message
   - Extract invoice information
   - Generate an invoice through TusFacturasApp
   - Send back the invoice details and PDF link

4. Use the Chat API at `/chat/send` for direct text interaction with the AI assistant.

## Deployment

### Deploying to Google Cloud Functions

1. Edit `deploy_functions.sh` and update the `PROJECT_ID` with your Google Cloud project ID:
   ```bash
   PROJECT_ID="your-project-id"  # Replace with your Google Cloud project ID
   ```

2. Make sure you're authenticated with Google Cloud:
   ```bash
   gcloud auth login
   ```

3. Run the deployment script:
   ```bash
   ./deploy_functions.sh
   ```

4. The script will:
   - Deploy the function to Google Cloud
   - Set up environment variables from your .env file
   - Display the function URL after deployment
   - Show the endpoints for WhatsApp webhook and Chat API

### Configuration Options

The deployment script provides several configuration options:
- `REGION`: The Google Cloud region (default: us-central1)
- `MEMORY`: Memory allocation (default: 512MB)
- `TIMEOUT`: Function timeout (default: 300s / 5 minutes)
- `MIN_INSTANCES`: Minimum instances (default: 0)
- `MAX_INSTANCES`: Maximum instances (default: 5)

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

This project uses:
- Black for code formatting
- Ruff for linting
- MyPy for type checking

Run the formatters:
```bash
black .
ruff check .
mypy .
```

## Project Structure

```
facturai/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── endpoints/       # API route handlers
│   │   └── router.py        # Main API router
│   ├── main.py              # FastAPI application
│   ├── console_chat.py      # Console chat interface
│   ├── models/              # Data models
│   └── services/            # Business logic
│       ├── ai_service.py    # AI processing
│       ├── whatsapp_service.py  # WhatsApp integration
│       └── tusfacturas_service.py  # Invoice generation
├── main_functions.py        # Cloud Functions entry point
├── deploy_functions.sh      # Cloud Functions deployment script
├── tests/                   # Test files
├── requirements.txt         # Project dependencies
├── .gcloudignore            # Files to ignore in Cloud deployment
└── README.md                # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

- All sensitive data is stored in environment variables
- WhatsApp webhook verification is implemented
- Secure API communication with TusFacturasApp
- No sensitive data is logged

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 