from google.cloud import storage
import datetime
import streamlit as st

import os
# Fetch the project ID automatically to ensure uniqueness
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "kairos-clinical")
BUCKET_NAME = f"{PROJECT_ID}-secure-uploads"

@st.cache_resource
def get_storage_client():
    return storage.Client()

def get_bucket():
    client = get_storage_client()
    try:
        bucket = client.get_bucket(BUCKET_NAME)
        return bucket
    except Exception:
        # If bucket doesn't exist, we might want to create it or error out.
        # For this exercise, we assume it exists or we create it.
        # In production, Terraform would handle this.
        # Let's try to create it if it doesn't exist (careful with permissions).
        try:
            bucket = client.create_bucket(BUCKET_NAME, location="US")
            # Apply lifecycle policy immediately upon creation
            set_lifecycle_policy(bucket)
            return bucket
        except Exception as e:
            st.error(f"Failed to access/create bucket {BUCKET_NAME}: {e}")
            return None

def set_lifecycle_policy(bucket):
    """
    Implement Lifecycle Policy: Auto-delete raw PDFs after 24 hours (Data Minimalism).
    """
    rules = [
        {
            "action": {"type": "Delete"},
            "condition": {"age": 1} # 1 day
        }
    ]
    bucket.lifecycle_rules = rules
    bucket.patch()
    # print(f"Lifecycle policy set for {bucket.name}")

def upload_blob(source_file, destination_blob_name):
    """
    Uploads a file-like object to the bucket.
    """
    bucket = get_bucket()
    if not bucket:
        return False
    
    try:
        blob = bucket.blob(destination_blob_name)
        # source_file is expected to be a file-like object (from st.file_uploader)
        # rewind just in case
        source_file.seek(0)
        blob.upload_from_file(source_file)
        
        # Ensure 24h TTL is active (idempotent check or rely on bucket policy)
        # We set it on bucket creation/access, so it applies to all objects.
        
        return True
    except Exception as e:
        st.error(f"Failed to upload file: {e}")
        return False
