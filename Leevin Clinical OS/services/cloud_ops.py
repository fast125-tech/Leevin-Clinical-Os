from google.cloud import firestore
from google.cloud import secretmanager
import datetime

def get_firestore_client():
    return firestore.Client()

def get_secret_manager_client():
    return secretmanager.SecretManagerServiceClient()

def log_audit_event(user: str, action: str, project: str, details: str):
    """
    Logs an audit event to Firestore 'audit_trails' collection.
    """
    try:
        db = get_firestore_client()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        audit_entry = {
            "timestamp": timestamp,
            "user": user,
            "action": action,
            "project": project,
            "details": details
        }
        
        db.collection("audit_trails").add(audit_entry)
    except Exception as e:
        print(f"Failed to log audit event: {e}")

def get_secrets(secret_id: str, version_id: str = "latest"):
    """
    Fetch API keys from Google Secret Manager.
    """
    try:
        client = get_secret_manager_client()
        # Assuming project ID is available in env or default credentials
        import google.auth
        _, project_id = google.auth.default()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Failed to fetch secret {secret_id}: {e}")
        return None

def save_training_data(data: dict):
    """
    Saves human-edited protocol drafts to Firestore 'training_data' collection.
    """
    try:
        db = get_firestore_client()
        # Add server-side timestamp if not present, or just trust the one passed
        if "timestamp" not in data:
            data["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
        db.collection("training_data").add(data)
        return True
    except Exception as e:
        print(f"Failed to save training data: {e}")
        return False
