import streamlit as st
from modules.marketing_bot import post_to_linkedin, post_to_x
import random

st.set_page_config(page_title="KAIROS Admin", layout="wide", page_icon="🛡️")

st.image("logo.png", width=150)
st.title("KAIROS Clinical | Growth Engine")

# Split Layout
col_marketing, col_stats = st.columns([2, 1])

# Left Column: Marketing Engine
with col_marketing:
    st.subheader("🚀 Marketing Engine")
    st.markdown("---")
    
    audit_finding = st.text_area("Paste Successful Audit Finding / Success Story", height=150)
    
    if st.button("Draft Campaign"):
        st.info("Drafting content based on finding...")
        st.session_state['draft_linkedin'] = f"Success Story: {audit_finding[:50]}... #ClinicalTrials #AI"
        st.session_state['draft_x'] = f"Big win for AI in Clinical Ops! {audit_finding[:30]}... 🧵"
    
    if 'draft_linkedin' in st.session_state:
        st.text_area("LinkedIn Draft", value=st.session_state['draft_linkedin'], key="li_draft")
        if st.button("Post to LinkedIn"):
            if post_to_linkedin(st.session_state['li_draft']):
                st.success("Posted to LinkedIn!")
            else:
                st.error("Failed to post to LinkedIn.")

    if 'draft_x' in st.session_state:
        st.text_area("X (Twitter) Draft", value=st.session_state['draft_x'], key="x_draft")
        if st.button("Post to X"):
            if post_to_x(st.session_state['x_draft']):
                st.success("Posted to X!")
            else:
                st.error("Failed to post to X.")

# Right Column: Platform Stats
with col_stats:
    st.subheader("📊 Platform Stats")
    st.markdown("---")
    
    # Mock Metrics
    st.metric("Annual Recurring Revenue (ARR)", "$1.2M", "+12%")
    st.metric("Active Users (DAU)", "450", "+5%")
    st.metric("Server Status", "Healthy", "99.9% Uptime")
    
    st.markdown("### Recent Alerts")
    st.warning("High Load on Translation Service (2 mins ago)")
    st.success("Backup Completed (1 hour ago)")
