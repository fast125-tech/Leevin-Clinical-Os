
import streamlit as st
import os
import sys

import pandas as pd
# Add Services to Path
sys.path.append(os.path.join(os.getcwd(), 'services'))
sys.path.append(os.path.join(os.getcwd(), 'synthetic_data'))

from services.router import HybridRouter
from services.cdm_agent import CdmAgent
from services.auth_service import AuthService
try:
    from synthetic_data.generate_test import generate_stress_test_data
except ImportError:
    generate_stress_test_data = None

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Leevin OS | Trinity Edition", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS: BLUE/SILVER THEME ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #f8fafc; }
    
    /* Headers */
    h1, h2, h3 { 
        color: #1e3a8a; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 700; 
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Cards */
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Matrix Badge */
    .matrix-badge {
        background-color: #1e3a8a;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# --- AUTHENTICATION FLOW ---
def login():
    st.markdown("## 🛡️ Leevin OS Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = AuthService.login(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user_role = user['role']
            st.session_state.user_name = user['name']
            st.rerun()
        else:
            st.error("Invalid Username or Password")
            
def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.rerun()

# --- MAIN APP LOGIC ---
if not st.session_state.authenticated:
    # Centered Login Container
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        login()
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("Default Credentials: admin / 123 or user / 123")
else:
    # --- LOGGED IN UI ---
    
    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/medical-doctor.png", width=60)
        st.title("Leevin OS")
        st.caption(f"Welcome, {st.session_state.user_name}")
        st.caption(f"Role: {st.session_state.user_role}")
        st.divider()
        
        # dynamic_modules based on role
        allowed_modules = AuthService.get_modules_by_role(st.session_state.user_role)
        module = st.radio("Select Module", allowed_modules)
        
        st.divider()
        st.markdown("**Brain Status:**")
        st.markdown("🟢 Brain 1 (Logic): Active")
        st.markdown("🟡 Brain 2 (BERT): Loading...")
        st.markdown("🔵 Brain 3 (Gemini): Standby")
        
        st.divider()
        if st.button("Logout"):
            logout()

    # --- ROUTER ---
    if module == "Dashboard":
        st.header("🏥 Clinical Command Center")
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Studies", "4")
        c2.metric("Pending Clean", "12 Files")
        c3.metric("Coding Queue", "85 Terms")
        
        st.markdown("### System Philosophy: Tri-Hybrid Intelligence")
        st.info("Leevin OS routes tasks to the most efficient brain: Deterministic Logic (Free), Specialist BERT (Fast), or Generative Gemini (Smart).")

    elif module == "Module 1: The Cleaner":
        st.header("🧹 The Cleaner: Data Validation")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("Upload Raw EDC Dump (CSV) for validation.")
        f = st.file_uploader("Upload CSV", type=["csv", "xlsx"])
        
        if f:
            # 1. Router
            f_type, content = HybridRouter.identify_and_read(f)
            
            if f_type == "DATAFRAME":
                st.info(f"📂 File Recognized: Structured Data ({len(content)} rows)")
                st.dataframe(content.head(), use_container_width=True)
                
                if st.button("🚀 Run Tri-Hybrid Checks"):
                    agent = CdmAgent()
                    
                    # BRAIN 1: HARD CHECKS
                    with st.spinner("🤖 Brain 1 (The Enforcer) Scanning..."):
                        hard_issues = agent.run_hard_checks(content)
                    
                    # BRAIN 3: SOFT CHECKS
                    with st.spinner("🧠 Brain 3 (The Doctor) Reading Comments..."):
                        soft_issues = agent.run_soft_checks(content)
                        
                    # Display Report
                    c1, c2 = st.columns(2)
                    with c1:
                        st.error("Hard Check Results")
                        for i in hard_issues:
                             st.write(i)
                    with c2:
                        st.warning("Soft Check Results")
                        for i in soft_issues:
                             st.write(i)
                             
            elif f_type == "TEXT":
                st.info("📂 File Recognized: Unstructured Text (PDF)")
                st.text_area("Preview", content[:500])
                st.warning("PDF Analysis module (Protocol Digitizer) is in 'Brain 3' standby.")
            else:
                st.error("❌ Unknown File Type.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif module == "Module 2: The Auto-Coder":
        st.header("💊 The Auto-Coder (Bio_ClinicalBERT)")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Import Service Locally to save startup time for other pages
        try:
            from services.bert_service import ClinicalBertService
            bert = ClinicalBertService()
            st.sidebar.markdown("🟢 Brain 2 (BERT): Active")
        except Exception as e:
            st.error(f"BERT Engine Offline: {e}")
            bert = None

        term = st.text_input("Enter Adverse Event Term", "Patient complains of severe migraine")
        if st.button("Code Term"):
            if bert:
                # Mock Dictionary for Demo
                meddra_dict = ["Headache", "Migraine", "Nausea", "Vomiting", "Fatigue", "Dizziness"]
                
                with st.spinner("🧠 BERT Vectorizing..."):
                    res = bert.auto_code_adverse_event(term, meddra_dict)
                
                c1, c2 = st.columns(2)
                c1.metric("Best Match", res['Match'])
                c2.metric("Confidence", f"{res['Confidence']*100:.1f}%")
                
                if res['Status'] == "Auto-Coded":
                    st.success(f"✅ Auto-Accepted ({res['Status']})")
                else:
                    st.warning(f"⚠️ Flagged for Human Review ({res['Status']})")
        st.markdown('</div>', unsafe_allow_html=True)

    elif module == "Module 3: The Builder":
        st.header("🛠️ The Builder: UAT Generator")
        st.info("Generate 'Stress Test' data to prove the system's fault tolerance.")
        
        rows = st.slider("Number of Subjects", 10, 500, 50)
        
        if st.button("Generate Stress Data"):
            if generate_stress_test_data:
                with st.spinner("Generating dirty data..."):
                    stress_df = generate_stress_test_data(rows)
                    st.success(f"Generated {len(stress_df)} rows with intentional errors.")
                    
                    st.dataframe(stress_df.head(10))
                    
                    # CSV Download
                    csv = stress_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Stress CSV",
                        csv,
                        "stress_test_data.csv",
                        "text/csv",
                        key='download-csv'
                    )
            else:
                st.error("Generator Script Not Found.")

    # --- FOOTER ---
    st.markdown("---")
    st.caption("Leevin Clinical OS | Powered by Hybrid Intelligence")
