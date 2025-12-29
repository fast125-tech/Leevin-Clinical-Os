import streamlit as st
import pandas as pd
import io

# Logic Imports
from logic.agent_logic import generate_dmp, generate_acrf_map, generate_uat_script
from logic.data_cleaner import DataCleaner
from logic.reconciler import Reconciler
from logic.sdtm_engine import auto_map_to_sdtm, validate_sdtm_structure
from logic.security_agent import SecuritySentinel
from logic.vendor_quality import VendorScorecard
from logic.uat_engine import generate_synthetic_uat_data
from logic.uat_validator import validate_uat_results, generate_evidence_report, generate_metrics_chart
from logic.edit_check_engine import EditCheckExecutor
from logic.hybrid_router import HybridBrain

def render_cdm_dashboard(sentinel):
    st.title("🧼 Data Command Center")
    
    # Revised Tabs
    tab_setup, tab_build, tab_clean, tab_recon, tab_sdtm = st.tabs([
        "Study Setup", "Database Build", "Cleaner", "Reconciler", "🏭 SDTM Factory"
    ])
    
    cleaner = DataCleaner()
    reconciler = Reconciler()
    
    # --- TAB: STUDY SETUP ---
    with tab_setup:
        st.header("🚀 Study Setup (The Architect)")
        col_dmp, col_acrf = st.columns(2)
        
        with col_dmp:
            st.subheader("Auto-DMP")
            st.info("Generates Data Management Plan from Protocol.")
            dmp_file = st.file_uploader("Upload Protocol (PDF)", type=["pdf"], key="dmp_up")
            if dmp_file and st.button("Generate DMP"):
                with st.status("📝 Drafting Plan...", expanded=True):
                    res = generate_dmp(dmp_file)
                    st.success("DMP Generated!")
                st.warning("⚠️ **Human Verification Required**: Review DMP logic before approval.")
                st.markdown(res)
                st.download_button("Download DMP", res, "dmp.md")
        
        with col_acrf:
            st.subheader("aCRF Mapper")
            st.info("Maps Blank CRFs to CDISC SDTM Variables.")
            acrf_file = st.file_uploader("Upload Blank CRF (PDF)", type=["pdf"], key="acrf_up")
            if acrf_file and st.button("Map Variables"):
                 with st.status("🗺️ Mapping Fields...", expanded=True):
                     res = generate_acrf_map(acrf_file)
                     st.success("Mapping Complete!")
                 st.warning("⚠️ **Human Verification Required**: Verify SDTM mapping compliance.")
                 st.markdown(res)

    # --- TAB: DATABASE BUILD (NEW) ---
    with tab_build:
        st.header("🏗️ Database UAT Builder (Module 2)")
        st.info("Generate User Acceptance Testing (UAT) Data for EDC Build.")
        
        # UI for UAT
        spec_file = st.file_uploader("Upload EDC Spec (Excel)", type=["xlsx"], key="uat_spec")
        
        output_type = st.radio("Output Type", ["Human Script (Excel)", "Machine Import File (CSV)"], horizontal=True)
        
        if spec_file and st.button("Generate UAT Data"):
             # Load spec
             try:
                 df_spec = pd.read_excel(spec_file)
             except Exception as e:
                 st.error(f"Error reading Excel: {e}")
                 st.stop()
                 
             if output_type == "Human Script (Excel)":
                 with st.status("🤖 Writing Script...", expanded=True):
                     st.write("Using Agent Logic to write test steps...")
                     # agent_logic.generate_uat_script expects a DataFrame, originally CDISC dataframe
                     # Here we pass the Spec DF. The AI prompt in generate_uat_script handles generic DF text
                     res_bytes = generate_uat_script(df_spec)
                     st.success("Script Generated!")
                     
                 st.download_button("Download Script (.xlsx)", res_bytes, "uat_script.xlsx")
                 
             else:
                 # Machine Import Logic
                 with st.status("⚙️ Generating Synthetic Data...", expanded=True):
                     st.write("Creating Scenarios (Clean, Boundary, Failure)...")
                     df_synth = generate_synthetic_uat_data(df_spec)
                     st.success(f"Generated {len(df_synth)} Test Records.")
                     
                 st.dataframe(df_synth.head())
                 csv_synth = df_synth.to_csv(index=False).encode('utf-8')
                 st.download_button("Download Import File (.csv)", csv_synth, "synthetic_uat_data.csv")

        # --- STEP 3: VALIDATE & REPORT ---
        st.divider()
        st.subheader("Step 3: Validate & Report (Evidence)")
        col_v1, col_v2 = st.columns(2)
        
        # We need the Expected Data (often the Synthetic Data just generated)
        # For flow, we ask user to upload it again or use state? 
        # Upload is safer for statelessness.
        expected_file = col_v1.file_uploader("Upload Expected Data (Synthetic)", type=["csv"], key="uat_exp")
        actual_file = col_v2.file_uploader("Upload Actual Export (EDC)", type=["csv"], key="uat_act")
        
        if expected_file and actual_file and st.button("Run Validation Certificate"):
            df_exp = pd.read_csv(expected_file)
            df_act = pd.read_csv(actual_file)
            
            with st.status("🔍 Verifying Data Points...", expanded=True):
                res_df = validate_uat_results(df_exp, df_act)
                html_report = generate_evidence_report(res_df)
                st.success("Validation Complete!")
                
            # Metrics
            total = len(res_df)
            passed = len(res_df[res_df['ValidationStatus'] == "PASS"])
            failed = total - passed
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Tests", total)
            m2.metric("Pass Rate", f"{round(passed/total*100,1)}%")
            m3.metric("Failed", failed, delta=-failed if failed > 0 else 0)
            
            # Chart (Plotly)
            fig = generate_metrics_chart(res_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Failures View
            if failed > 0:
                st.error("Failures Detected:")
                st.dataframe(res_df[res_df['Status'] == "FAIL"])
            else:
                st.balloons()
            
            # Download
            st.download_button("🏆 Download Certificate (.html)", html_report, "UAT_Validation_Cert.html", "text/html")

    # --- TAB: CLEANER ---
    with tab_clean:
        st.header("Hybrid Data Cleaning")
        csv = st.file_uploader("Upload EDC Data (CSV)", type=["csv"], key="clean_up")
        
        if csv:
            df = pd.read_csv(csv)
            # SECURITY SCAN
            is_safe, msg = sentinel.scan_dataframe(df, csv.name, "Data Manager")
            if not is_safe:
                st.error(msg)
                st.stop()
            
            st.success("✅ Security Scan Passed")
            st.dataframe(df.head())
            
            if st.button("Run Medical Logic Check"):
                 # --- HYBRID ROUTER INTEGRATION ---
                 secure_mode = st.checkbox("🔒 Secure Mode (Local MedGemma Scrub)")
                 
                 if secure_mode:
                     hb = HybridBrain()
                     with st.status("🛡️ Hybrid Agentic Workflow...", expanded=True) as status:
                         st.write("🏠 Local Brain: Scrubbing PII (Ollama/MedGemma)...")
                         text_blob = df.head().to_string()
                         sanitized_text, analysis = hb.process_sensitive_patient_data(text_blob)
                         
                         st.write("☁️ Cloud Brain: Analyzing Clinical Logic (Vertex AI)...")
                         status.update(label="✅ Hybrid Processing Complete", state="complete")
                     
                     with st.expander("📄 View Sanitized Data (Proof of Privacy)"):
                         st.code(sanitized_text)
                         
                     st.subheader("Cloud Analysis")
                     st.markdown(analysis)
                     
                 else:
                     with st.status("👩‍⚕️ Analyzing Medical Logic...", expanded=True) as status:
                         st.write("🔬 Checking Concomitant Meds...")
                         st.write("⚠️ Validating Adverse Events...")
                         res = cleaner.run_medical_consistency(df, df)
                         status.update(label="✅ Analysis Done", state="complete")
                     st.warning("⚠️ **Human Verification Required**: Verify clinical logic.")
                     st.markdown(res)
        
        st.divider()
        with st.expander("📋 Spec-Based Validation (No-Code Engine)", expanded=False):
            st.info("Upload your Data Validation Plan (Excel) to auto-execute Python edits.")
            col_spec, col_data = st.columns(2)
            spec_file = col_spec.file_uploader("Upload Spec (Excel)", type=["xlsx"])
            data_file = col_data.file_uploader("Upload Data (CSV) for Validation", type=["csv"])
            
            if spec_file and data_file and st.button("Run Edit Checks"):
                executor = EditCheckExecutor()
                with st.status("⚙️ Engine Running...", expanded=True) as status:
                    df_discrepancies = executor.run_spec_based_checks(data_file, spec_file)
                    status.update(label="✅ Validation Complete", state="complete")
                    
                if not df_discrepancies.empty:
                     st.error(f"❌ Found {len(df_discrepancies)} Discrepancies")
                     st.dataframe(df_discrepancies)
                     csv = df_discrepancies.to_csv(index=False).encode('utf-8')
                     st.download_button("Export Discrepancy Log (.csv)", csv, "discrepancies.csv", "text/csv")
                else:
                    st.success("✅ Clean Sweep! No discrepancies found.")

    # --- TAB: RECONCILER ---
    with tab_recon:
        st.header("Safety Reconciler")
        with st.expander("🏆 Vendor Scorecard (Quality Leaderboard)", expanded=True):
             vq = VendorScorecard()
             leaderboard = vq.get_leaderboard()
             st.dataframe(leaderboard if not leaderboard.empty else pd.DataFrame(), use_container_width=True)
        
        ae_file = st.file_uploader("AE Dataset", type=["csv"], key="ae")
        ds_file = st.file_uploader("DS Dataset", type=["csv"], key="ds")
        
        if ae_file and ds_file and st.button("Triangulate Safety Data"):
             df_ae = pd.read_csv(ae_file)
             df_ds = pd.read_csv(ds_file)
             # Mock scan
             sentinel.scan_dataframe(df_ae, "AE", "Data Manager")
             
             vq.log_upload_quality("Vendor_A", len(df_ae), 0)
             res = reconciler.run_safety_triangulation(df_ae, df_ds, pd.DataFrame())
             st.dataframe(res)

    # --- TAB: SDTM FACTORY ---
    with tab_sdtm:
        st.header("🏭 SDTM Factory (Module 9)")
        st.info("Automated conversion of Raw Data to CDISC SDTM 3.3 Drafts.")
        col_1, col_2 = st.columns(2)
        with col_1: target_domain = st.selectbox("Target Domain", ["DM", "VS", "AE", "LB", "MH"])
        with col_2: raw_file = st.file_uploader("Upload Raw Data (CSV)", type=["csv"], key="sdtm_up")
        
        if raw_file and st.button("Auto-Map & Convert"):
             with st.status("🏭 Factory Running...", expanded=True):
                 import os
                 temp_path = f"temp_{raw_file.name}"
                 with open(temp_path, "wb") as f: f.write(raw_file.getbuffer())
                 df_sdtm, log = auto_map_to_sdtm(temp_path, target_domain)
                 report = validate_sdtm_structure(df_sdtm, target_domain)
                 st.success(log)
                 st.info(report)
                 if os.path.exists(temp_path): os.remove(temp_path)
             
             st.warning("⚠️ **Human Verification Required**: SDTM mappings are drafts.")
             st.dataframe(df_sdtm)
             csv_sdtm = df_sdtm.to_csv(index=False).encode('utf-8')
             st.download_button(f"Download {target_domain} (SDTM)", csv_sdtm, f"sdtm_{target_domain}.csv")
