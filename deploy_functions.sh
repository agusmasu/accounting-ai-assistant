#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="voicein-456423"  # Replace with your Google Cloud project ID
REGION="us-central1"          # Replace with your preferred region
FUNCTION_NAME="accounting-ai-assistant-chat"
ENTRY_POINT="send_message"
RUNTIME="python311"           # Using Python 3.11
MEMORY="512MB"
TIMEOUT="300s"                # 5 minutes
MIN_INSTANCES=0
MAX_INSTANCES=5
SOURCE="main_functions.py"

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

# Create a temp file with all env vars
ENV_VARS=""
if [ -f .env ]; then
    ENV_VARS=$(grep -v '^#' .env | tr '\n' ',')
    # Remove the trailing comma
    ENV_VARS=${ENV_VARS%,}
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
    --set-env-vars=$ENV_VARS

# Get the function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)")

echo ""
echo "Deployment successful!"
echo "Function URL: $FUNCTION_URL"
echo ""
echo "Chat API URL: $FUNCTION_URL"
echo ""
echo "Example usage:"
echo "curl -X POST $FUNCTION_URL -H \"Content-Type: application/json\" -d '{\"message\":\"your message here\"}'"
echo "" 