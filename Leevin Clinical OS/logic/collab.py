import streamlit as st
from services.cloud_ops import get_firestore_client
import datetime

def render_chat_sidebar(project_id, username):
    """
    Renders the project chat sidebar and handles message posting.
    """
    st.sidebar.markdown("### 💬 Project Chat")
    
    # Message Input
    msg = st.sidebar.text_input("Message", key="chat_input")
    if st.sidebar.button("Send", key="send_chat"):
        if msg:
            post_comment(project_id, username, msg)
            st.sidebar.success("Sent!")
            st.rerun()
            
    # Display Messages (Mock for now, normally fetch from Firestore)
    st.sidebar.markdown("---")
    st.sidebar.caption("Recent Activity")
    st.sidebar.text(f"[{datetime.datetime.now().strftime('%H:%M')}] {username}: {msg}" if msg else "No recent messages.")

def post_comment(project_id, user, text):
    """
    Saves a comment to Firestore.
    """
    try:
        db = get_firestore_client()
        comment = {
            "project_id": project_id,
            "user": user,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        db.collection("project_comments").add(comment)
        
        # Check for tasks
        if "Action Item:" in text:
            task_text = text.split("Action Item:")[1].strip()
            add_task(project_id, task_text, "Pending", user)
            
    except Exception as e:
        print(f"Failed to post comment: {e}")

def add_task(project_id, description, status, owner):
    """
    Adds a task to the project task list.
    """
    try:
        db = get_firestore_client()
        task = {
            "project_id": project_id,
            "description": description,
            "status": status,
            "owner": owner,
            "created_at": datetime.datetime.now().isoformat()
        }
        db.collection("tasks").add(task)
    except Exception as e:
        print(f"Failed to add task: {e}")
