
# DEPLOYMENT SCRIPT: Leevin OS (Cloud Run)
# Config: 4GB Memory for BERT | CPU Optimized

echo "🚀 Deploying Leevin OS (Trinity Edition)..."

# 1. Project Config
PROJECT_ID="kairos-clinical"
SERVICE_NAME="leevin-os-trinity"
REGION="us-central1"

# 2. Build & Deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project $PROJECT_ID \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --concurrency 40 \
  --timeout 300s \
  --set-env-vars="ENV=PRODUCTION,USE_BERT=TRUE"

echo "✅ Deployment Triggered."
