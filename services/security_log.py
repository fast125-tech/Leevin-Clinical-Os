import json
import os
import datetime

SECURITY_LOG_FILE = "security_audit.json"

def log_security_event(user, event_type, details, filename="N/A"):
    """
    Logs a security event to the local audit trail.
    """
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user,
        "event_type": event_type, # e.g., "PHI_BLOCK", "LOGIN", "UNAUTHORIZED_ACCESS"
        "details": details,
        "filename": filename
    }
    
    # Load existing log
    if os.path.exists(SECURITY_LOG_FILE):
        with open(SECURITY_LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []
        
    logs.append(entry)
    
    # Save back
    with open(SECURITY_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
        
    return True

def get_security_logs():
    """
    Retrieves all security logs.
    """
    if os.path.exists(SECURITY_LOG_FILE):
        with open(SECURITY_LOG_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []
