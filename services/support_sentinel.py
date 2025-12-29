import streamlit as st
from services.cloud_ops import get_firestore_client
from google.cloud import firestore
import datetime

class SupportSentinel:
    def __init__(self):
        self.kb = {
            "Upload Failed": "Please ensure your PDF is under 50MB and is not password protected.",
            "Translation Error": "The translation service is currently experiencing high load. Please try again in 5 minutes.",
            "Login Issue": "If you are locked out, please contact your study administrator to reset your credentials."
        }

    def get_recent_user_activity(self, project_id: str, limit: int = 5):
        """
        Returns the last N log entries for a specific project.
        """
        try:
            db = get_firestore_client()
            # In a real app, we'd also filter by user_id, but project_id is a good proxy for context
            docs = db.collection("audit_trails")\
                .where("project", "==", project_id)\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            # st.error(f"Sentinel Error: Could not fetch logs: {e}")
            return []

    def create_support_ticket(self, user: str, issue: str, priority: str = "Normal"):
        """
        Escalates to human team by creating a ticket in Firestore.
        """
        try:
            db = get_firestore_client()
            ticket = {
                "user": user,
                "issue": issue,
                "priority": priority,
                "status": "Open",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            db.collection("support_tickets").add(ticket)
            return True
        except Exception as e:
            st.error(f"Failed to create ticket: {e}")
            return False

    def handle_query(self, user_query: str, user: str, project_id: str):
        """
        Main behavior loop:
        1. Fetch logs.
        2. Correlate.
        3. Respond.
        """
        # 1. Fetch Logs
        logs = self.get_recent_user_activity(project_id)
        
        # 2. Analyze Logs for Errors
        recent_error = None
        for log in logs:
            # Simple heuristic: check for "Failed" or "Error" in action or details
            # In a real system, we'd have a status field
            if "Fail" in log.get('action', '') or "Error" in log.get('details', ''):
                recent_error = log
                break
        
        response = ""
        
        # 3. Correlate & Respond
        if recent_error:
            # Calculate time diff (mocking "2 minutes ago" logic)
            # timestamp = recent_error['timestamp']
            # ... time diff logic ...
            
            response += f"I see a recent issue: **{recent_error['action']}** ({recent_error['details']}). "
            
            # Check KB
            kb_solution = None
            for key, val in self.kb.items():
                if key in recent_error['action']:
                    kb_solution = val
                    break
            
            if kb_solution:
                response += f"\n\n**Suggestion:** {kb_solution}"
            else:
                response += "\n\nI don't have a specific fix for this in my Knowledge Base."
                
        else:
            response += "I don't see any recent system errors in the logs."

        # 4. Frustration / Critical Check (Simple keyword matching)
        critical_keywords = ["corrupt", "lost data", "urgent", "broken", "angry"]
        is_critical = any(k in user_query.lower() for k in critical_keywords)
        
        if is_critical or (recent_error and not kb_solution):
            response += "\n\nThis sounds important. I can escalate this to our human engineering team immediately."
            return {
                "response": response,
                "suggest_ticket": True
            }
            
        return {
            "response": response,
            "suggest_ticket": False
        }
