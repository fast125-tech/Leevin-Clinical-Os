#!/bin/bash

# Set Project ID
PROJECT_ID="leevin-clinical-os"
REGION="asia-south1" # Corrected from "AsiaSouth Mumbai"
SERVICE_NAME="kairos-app"

# --- SECURITY: PINECONE CREDENTIALS ---
echo "----------------------------------------------------"
echo "🔐 PINECONE SECURITY SETUP"
echo "----------------------------------------------------"

# Check if PINECONE_API_KEY is already set in environment
if [ -z "$PINECONE_API_KEY" ]; then
    echo "⚠️  PINECONE_API_KEY not found in environment."
    read -s -p "🔑 Enter your Pinecone API Key (hidden): " PINECONE_API_KEY
    echo ""
else
    echo "✅ PINECONE_API_KEY detected."
fi

# Check if PINECONE_ENV is already set
if [ -z "$PINECONE_ENV" ]; then
    echo "⚠️  PINECONE_ENV not found in environment."
    read -p "🌍 Enter your Pinecone Environment (e.g., gcp-starter): " PINECONE_ENV
else
    echo "✅ PINECONE_ENV detected."
fi

# Validation
if [ -z "$PINECONE_API_KEY" ] || [ -z "$PINECONE_ENV" ]; then
    echo "❌ Error: Missing Pinecone Credentials. Aborting."
    exit 1
fi
echo "----------------------------------------------------"

# Enable APIs
echo "🚀 Enabling Google Cloud APIs..."
gcloud services enable aiplatform.googleapis.com run.googleapis.com firestore.googleapis.com secretmanager.googleapis.com texttospeech.googleapis.com cloudbuild.googleapis.com

# Build Container
echo "🏗️  Building Container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run with Secrets
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --set-env-vars PINECONE_API_KEY="$PINECONE_API_KEY",PINECONE_ENV="$PINECONE_ENV"

echo "✅ Deployment Complete!"
