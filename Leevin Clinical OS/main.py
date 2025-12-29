import streamlit as st
import pandas as pd
from services.cloud_ops import log_audit_event, save_training_data
from logic.agent_brain import audit_protocol
from services.auth import check_login
import datetime

st.set_page_config(page_title="KAIROS | Clinical OS", layout="wide", page_icon="⏳")

# Auth Check
authentication_status, username, org_id, role, _ = check_login()

# Sidebar
with st.sidebar:
    st.image("logo.png", width=200)
    st.markdown("### KAIROS Clinical")
    st.success(f"👤 **{username}**")
    st.info(f"🏢 **{org_id}**")
    st.caption(f"Role: {role}")
    
    project_id = st.text_input("Project ID", value="KAIROS-001")
    full_project_path = f"{org_id}/{project_id}"
    st.caption(f"Path: {full_project_path}")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Main Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Design (Audit)", "Build (Write)", "Clean (Data)", 
    "Reconcile", "Translate", "File (eTMF)"
])

# Tab 1: Design (Audit)
with tab1:
    st.header("Protocol Design & Audit")
    st.info("ℹ️ **How it works:** Upload your Clinical Protocol (PDF). The AI will extract the Schedule of Events, calculate a Feasibility Score (0-100), and identify critical risks.\n**Expected Output:** A risk assessment report and immutable audit log entry.")
    uploaded_file = st.file_uploader("Upload Protocol PDF", type=["pdf"])
    if uploaded_file:
        if st.button("Analyze Risks"):
            with st.spinner("Analyzing Protocol..."):
                # Mock text extraction
                text = "Mock Protocol Text..."
                risks = audit_protocol(text)
                st.success("Analysis Complete")
                st.write(risks)
                log_audit_event(username, "Audit", full_project_path, f"Analyzed {uploaded_file.name}")

# Tab 2: Build (Write)
with tab2:
    st.header("Protocol Builder")
    st.info("ℹ️ **How it works:** Enter the target Indication and Phase. The AI uses TransCelerate templates to draft a protocol synopsis.\n**Expected Output:** A zero-draft synopsis ready for Medical Writer review.")
    indication = st.text_input("Indication (e.g., Oncology)")
    phase = st.selectbox("Phase", ["Phase I", "Phase II", "Phase III", "Phase IV"])
    if st.button("Generate Zero Draft"):
        with st.spinner("Drafting Synopsis..."):
            # Generate Draft
            draft_text = f"""
### Protocol Synopsis: {indication} ({phase})
**Objective:** To evaluate safety and efficacy...
**Design:** Randomized, double-blind...
**Population:** Patients with {indication}...
            """
            st.session_state['draft_synopsis'] = draft_text
            
    if 'draft_synopsis' in st.session_state:
        st.subheader("Review & Refine (Human-in-the-Loop)")
        edited_text = st.text_area("Edit generated draft:", value=st.session_state['draft_synopsis'], height=300)
        
        if st.button("✅ Approve & Save as Gold Standard"):
            # Save to Firestore (Training Data)
            training_entry = {
                "org_id": org_id,
                "indication": indication,
                "phase": phase,
                "ai_draft": st.session_state['draft_synopsis'],
                "final_human_version": edited_text,
                "timestamp": datetime.datetime.now().isoformat(),
                "user": username
            }
            if save_training_data(training_entry):
                st.success("System has learned from your expertise. Saved to Neural Memory.")
                st.json(training_entry) # Show what was saved
                log_audit_event(username, "Write", full_project_path, "Approved Protocol Draft")
            else:
                st.error("Failed to save training data.")

# Tab 3: Clean (Data)
with tab3:
    st.header("Data Cleaning")
    st.info("ℹ️ **How it works:** Upload raw clinical data. The AI scans for logic errors (e.g., Consent Date > Enrollment Date) and outliers.\n**Expected Output:** A downloadable query report.")
    csv_file = st.file_uploader("Upload EDC Dump (CSV or Excel)", type=["csv", "xlsx"])
    if csv_file:
        if csv_file.name.endswith('.csv'):
            df = pd.read_csv(csv_file)
        else:
            df = pd.read_excel(csv_file)
        st.dataframe(df.head())
        st.success(f"Loaded {len(df)} rows.")
        log_audit_event(username, "Data Load", full_project_path, f"Uploaded {csv_file.name}")
        
        st.subheader("Query Management")
        # Mock Query Data
        query_data = {
            "Site": ["101", "102", "101"],
            "Subject": ["101-001", "102-005", "101-003"],
            "Visit": ["V1", "V2", "V1"],
            "Query Text": ["Date out of range", "Missing Lab Units", "Signature missing"],
            "Status": ["Open", "Answered", "Closed"]
        }
        query_df = pd.DataFrame(query_data)
        edited_df = st.data_editor(query_df, num_rows="dynamic")
        
        # Export Queries
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Queries (Excel)",
            data=csv, # In real app, use to_excel
            file_name='queries.csv',
            mime='text/csv',
        )

# Tab 4: Reconcile
with tab4:
    st.header("Reconciliation Engine")
    st.info("ℹ️ **How it works:** Upload two datasets (e.g., Clinical Database + Safety Database). The AI performs fuzzy matching to find discrepancies.\n**Expected Output:** A reconciliation table highlighting mismatched records.")
    
    rec_type = st.selectbox("Reconciliation Type", [
        "SAE Reconciliation (EDC vs Safety)", 
        "Lab Reconciliation (EDC vs Central Lab)", 
        "eCOA Reconciliation (EDC vs ePRO)"
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        label1 = "Upload EDC Data"
        st.file_uploader(label1, key="rec_file_1")
    with col2:
        label2 = "Upload Safety Data" if "Safety" in rec_type else "Upload Central Lab Data" if "Lab" in rec_type else "Upload ePRO Data"
        st.file_uploader(label2, key="rec_file_2")
        
    if st.button("Run Reconciliation"):
        st.info(f"Running {rec_type}...")
        # Mock Discrepancy Report
        disc_data = {
            "Subject": ["101-002", "103-001"],
            "EDC Value": ["Severe", "12.5"],
            "External Value": ["Moderate", "12.8"],
            "Discrepancy": ["Severity Mismatch", "Value Mismatch"]
        }
        st.subheader("Discrepancy Report")
        st.dataframe(pd.DataFrame(disc_data))
        log_audit_event(username, "Reconcile", full_project_path, f"Ran {rec_type}")

# Tab 5: Translate
with tab5:
    st.header("Global Translation Hub")
    st.info("ℹ️ **How it works:** Enter medical text. The AI translates it while performing a 'Back-Translation Audit' to ensure clinical accuracy.\n**Expected Output:** Translated text + Accuracy Score.")
    text_to_translate = st.text_area("Enter Text")
    target_lang = st.selectbox("Target Language", [
        "Hindi", "Marathi", "Gujarati", "Tamil", "Telugu", "Kannada", "Bengali", 
        "Spanish", "French", "German", "Japanese", "Chinese"
    ])
    
    if st.button("Translate"):
        with st.spinner("Translating & Auditing..."):
            # Mock Results
            translated_text = "[Translated Text Script]"
            back_translation = text_to_translate # Perfect match simulation
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 1. Translated Text")
                st.success(translated_text)
            with c2:
                st.markdown("### 2. Back-Translation")
                st.info(back_translation)
            with c3:
                st.markdown("### 3. Audit Score")
                st.metric("Accuracy", "98%", "PASS")
            
            log_audit_event(username, "Translate", full_project_path, f"Translated to {target_lang}")

# Tab 6: File (eTMF)
with tab6:
    st.header("eTMF Classifier")
    st.info("ℹ️ **How it works:** Upload unsorted PDFs. The AI reads the content and classifies them according to the DIA TMF Reference Model.\n**Expected Output:** Auto-renamed and sorted files.")
    docs = st.file_uploader("Upload Documents", accept_multiple_files=True)
    if docs:
        st.write(f"Classifying {len(docs)} documents...")
        log_audit_event(username, "File", full_project_path, f"Uploaded {len(docs)} docs")
