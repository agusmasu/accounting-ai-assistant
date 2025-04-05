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
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_VERIFY_TOKEN=your_verify_token

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# TusFacturasApp Configuration
TUSFACTURAS_USER_TOKEN=your_tusfacturas_user_token
TUSFACTURAS_API_TOKEN=your_tusfacturas_api_token
TUSFACTURAS_API_KEY=your_tusfacturas_api_key
```

## Usage

1. Start the application:
```bash
uvicorn app.main:app --reload
```

2. Configure your WhatsApp webhook to point to your server's `/webhook/whatsapp` endpoint.

3. Send a voice message to your WhatsApp number with the invoice details.

4. The bot will:
   - Process the voice message
   - Extract invoice information
   - Generate an invoice through TusFacturasApp
   - Send back the invoice details and PDF link

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
│   ├── main.py              # FastAPI application
│   ├── models/              # Data models
│   └── services/            # Business logic
│       ├── ai_service.py    # AI processing
│       ├── whatsapp_service.py  # WhatsApp integration
│       └── tusfacturas_service.py  # Invoice generation
├── tests/                   # Test files
├── requirements.txt         # Project dependencies
└── README.md               # This file
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