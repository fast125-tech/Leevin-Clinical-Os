#!/bin/bash
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/kairos-os
gcloud run deploy kairos-os --platform managed --allow-unauthenticated
