import streamlit as st
import pandas as pd
from logic.oncology_engine import OncologyEngine
from logic.recist_engine import RecistCalculator

def render_oncology_dashboard():
    st.header("🧬 Oncology Command Center")
    
    # Initialize Engines
    engine = OncologyEngine()
    recist = RecistCalculator()
    
    tab1, tab2, tab3 = st.tabs(["RECIST 1.1 Calculator", "Survival Tracker", "Toxicity Watch"])
    
    with tab1:
        st.subheader("📏 RECIST 1.1 Strict Mode")
        st.info("Strict mode calculator for tumor response evaluation (Target, Non-Target, and New Lesions).")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 1. Baseline Lesions")
            if 'lesions' not in st.session_state:
                st.session_state.lesions = []
                
            with st.form("add_lesion"):
                l_type = st.selectbox("Type", ["Solid", "Node"])
                size = st.number_input("Size (mm)", min_value=0.0)
                organ = st.text_input("Organ")
                if st.form_submit_button("Add Lesion"):
                    st.session_state.lesions.append({"type": l_type, "size": size, "organ": organ})
                    st.success("Added")
            
            # Display & Validate
            if st.session_state.lesions:
                st.table(st.session_state.lesions)
                validation = recist.validate_baseline(st.session_state.lesions)
                
                if validation['rejected']:
                    for err in validation['rejected']:
                        st.error(f"❌ Rejection: {err}")
                
                base_sum = validation['baseline_sum']
                st.metric("Baseline Sum (SOD)", f"{base_sum} mm")
        
        with col2:
            st.markdown("### 2. Current Timepoint")
            curr_sum = st.number_input("Current Sum of Target Lesions (mm)", min_value=0.0)
            
            st.markdown("### 3. Non-Target & New")
            nt_resp = st.selectbox("Non-Target Response", ["CR", "Non-CR/Non-PD", "PD"])
            new_lesion = st.checkbox("New Lesions Present?")
            
            if st.button("Calculate Overall Response"):
                # 1. Target Response
                t_resp = recist.calculate_target_response(base_sum, curr_sum)
                
                # 2. Overall Response
                ovr_resp = recist.determine_overall_response(t_resp, nt_resp, new_lesion)
                
                # Visualization
                color = "green" if ovr_resp in ["CR", "PR"] else "orange" if ovr_resp == "SD" else "red"
                st.markdown(f"## Overall Response: :{color}[{ovr_resp}]")
                st.info(f"Target Response: {t_resp} | Non-Target: {nt_resp} | New Lesions: {new_lesion}")

    with tab2:
        st.subheader("Survival & Follow-up Tracker")
        st.info("Analyzes patient follow-up data to flag patients at risk of being lost to follow-up.")
        st.info("Upload Patient Status Data (CSV)")
        uploaded_file = st.file_uploader("Upload Patient Data", type=["csv"], key="surv_up")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
            
            if st.button("Run Survival Scan"):
                risks = engine.check_survival_status(df)
                if not risks.empty:
                    st.error(f"🚩 Found {len(risks)} Patients potentially Lost to Follow-up!")
                    st.dataframe(risks)
                else:
                    st.success("✅ All patients accounted for within 90 days.")

    with tab3:
        st.subheader("Safety & Toxicity Cross-Check")
        st.info("Correlates lab results (LB) with exposure data (EX) to validate dose reductions.")
        st.write("Upload Lab Data (LB) and Exposure Data (EX) to validate Dose Reductions.")
        # Placeholder
