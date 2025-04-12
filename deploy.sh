#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="voicein-456423"  # Replace with your Google Cloud project ID
REGION="us-central1"          # Replace with your preferred region
FUNCTION_NAME="whatsapp-webhook"
ENTRY_POINT="whatsapp_webhook_function"
RUNTIME="python310"           # Updated to Python 3.10
MEMORY="256MB"
TIMEOUT="60s"
MIN_INSTANCES=0
MAX_INSTANCES=10

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "You are not logged in to gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Make sure to set environment variables manually."
fi

# Deploy the function
echo "Deploying function $FUNCTION_NAME..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --allow-unauthenticated \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --min-instances=$MIN_INSTANCES \
    --max-instances=$MAX_INSTANCES \
    --set-env-vars="OPENAI_API_KEY=$OPENAI_API_KEY,WHATSAPP_TOKEN=$WHATSAPP_TOKEN,WHATSAPP_VERIFY_TOKEN=$WHATSAPP_VERIFY_TOKEN"

# Get the function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)")

echo ""
echo "Deployment successful!"
echo "Function URL: $FUNCTION_URL"
echo ""
echo "WhatsApp Webhook URL: $FUNCTION_URL/webhook/whatsapp"
echo ""
echo "Verify Token: $(grep WHATSAPP_VERIFY_TOKEN .env | cut -d '=' -f2)"
echo ""
echo "Add this URL to your WhatsApp webhook configuration."
echo "Make sure to use the verify token from your .env file." 