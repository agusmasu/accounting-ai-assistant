#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="voicein-456423"  # Replace with your Google Cloud project ID
REGION="us-central1"          # Replace with your preferred region
FUNCTION_NAME="test-function"
ENTRY_POINT="test_function"
RUNTIME="python310"

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

# Deploy the function
echo "Deploying test function $FUNCTION_NAME..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --allow-unauthenticated

# Get the function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format="value(serviceConfig.uri)")

echo ""
echo "Deployment successful!"
echo "Test Function URL: $FUNCTION_URL" 