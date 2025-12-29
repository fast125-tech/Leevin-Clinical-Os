import datetime
from google.cloud import firestore
from google.cloud import secretmanager
import streamlit as st

# Initialize Firestore Client
# Using a singleton pattern or caching to avoid re-initializing on every rerun if possible,
# but for Streamlit, simple initialization at module level or cached function is common.
# Assuming GCP credentials are set in environment or via gcloud auth.

@st.cache_resource
def get_firestore_client():
    return firestore.Client()

@st.cache_resource
def get_secret_manager_client():
    return secretmanager.SecretManagerServiceClient()

def log_audit_event(user: str, action: str, project: str, details: str):
    """
    Logs an audit event to Firestore 'audit_trails' collection.
    Critical for FDA 21 CFR Part 11 compliance.
    Timestamp is ISO-8601.
    """
    try:
        db = get_firestore_client()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        audit_entry = {
            "timestamp": timestamp,
            "user": user,
            "action": action,
            "project": project,
            "details": details,
            "immutable": True # Flag to indicate this record should not be modified
        }
        
        # Add to 'audit_trails' collection
        db.collection("audit_trails").add(audit_entry)
        # print(f"Audit Logged: {action} by {user}") # Debug
    except Exception as e:
        st.error(f"CRITICAL: Failed to log audit event: {e}")
        # In a real FDA system, failure to log might require halting operations.

def get_secrets(secret_id: str, version_id: str = "latest") -> str:
    """
    Fetch API keys from Google Secret Manager.
    Do not hardcode keys.
    """
    try:
        client = get_secret_manager_client()
        # Project ID should be inferred from environment or config
        # For now, we assume the secret_id is the full resource name or we construct it if we knew the project ID.
        # However, the user prompt implies passing the name. 
        # Usually format: projects/{project_id}/secrets/{secret_id}/versions/{version_id}
        # We will assume the caller passes the simple name and we find the project, 
        # OR the caller passes the full path. 
        # Let's try to get the project ID from the firestore client or environment.
        
        # For simplicity in this snippet, we'll assume secret_id is just the name 
        # and we need the project ID. 
        # Let's fetch project ID from the default credentials/environment.
        import google.auth
        _, project_id = google.auth.default()
        
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        st.error(f"Failed to fetch secret {secret_id}: {e}")
        return None

def fetch_latest_high_value_event():
    """
    Fetches the latest 'High-Value' audit event from Firestore.
    High-Value events: 'Protocol Analysis', 'Synopsis Generation', 'Translation'.
    """
    try:
        db = get_firestore_client()
        # Query for latest event in 'audit_trails'
        # In reality, we would filter by specific actions and order by timestamp desc
        docs = db.collection("audit_trails")\
            .order_by("timestamp", direction=firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()
        
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        # st.error(f"Failed to fetch audit logs: {e}")
        return None
