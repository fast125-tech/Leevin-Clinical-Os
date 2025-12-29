import streamlit as st
import pandas as pd
import plotly.express as px
from logic.leevin_central import LeevinCentral

st.set_page_config(page_title="Leevin Clinical OS v1.6", layout="wide", page_icon="🧬")
central = LeevinCentral()

with st.sidebar:
    st.title("Leevin OS v1.6")
    role = st.radio("Select Persona", ["👩‍💻 CDM", "🕵️ CRA", "🏥 Site", "💊 Coder", "📝 Writer"])

# --- CDM VIEW ---
if role == "👩‍💻 CDM":
    st.header("👩‍💻 Lead CDM Console (v1.6)")
    # User requested "📋 PDs" tab
    tabs = st.tabs(["💊 SAE", "🧪 Labs", "☠️ Death", "📚 Coding", "🔄 AE-CM", "🏛️ MH-CM", "❓ Queries", "📋 PDs"])
    modes = ["SAE", "Labs", "Death", "Coding", "AE_ConMed", "MH_ConMed", "Query_Recon", "PD_Recon"]
    
    for i, t in enumerate(tabs):
        with t:
            mode = modes[i]
            st.subheader(f"{mode} Dashboard")
            c1, c2 = st.columns(2)
            
            # Custom labels for PD Recon
            l1 = "PD Log (CSV)" if mode == "PD_Recon" else "Primary File"
            l2 = "EDC Visits (CSV)" if mode == "PD_Recon" else "Compare File"
            
            f1 = c1.file_uploader(l1, key=f"f1_{mode}")
            # Query_Recon only needs 1 file. PD_Recon needs 2.
            f2 = c2.file_uploader(l2, key=f"f2_{mode}") if mode != "Query_Recon" else None
            
            if f1 and (f2 or mode == "Query_Recon") and st.button(f"Run Analysis", key=f"btn_{mode}"):
                df1 = pd.read_csv(f1)
                df2 = pd.read_csv(f2) if f2 else None
                res, metrics = central.cdm.run_recon(df1, df2, mode)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Records", metrics["Total"])
                m2.metric("Discrepancies", metrics["Issues"])
                m3.metric("Error Rate", f"{metrics['Rate']:.1f}%")
                
                if metrics["Issues"] > 0:
                    charts = central.cdm.visualize_metrics(res, mode)
                    if charts:
                        p1, p2 = st.columns(2)
                        if 'pie' in charts: p1.plotly_chart(charts['pie'], use_container_width=True)
                        if 'bar' in charts: p2.plotly_chart(charts['bar'], use_container_width=True)
                
                st.dataframe(res, use_container_width=True)
                st.download_button(f"💾 Download CSV", res.to_csv(index=False).encode('utf-8'), f"{mode}.csv", "text/csv")

# --- CRA VIEW ---
elif role == "🕵️ CRA":
    st.header("🕵️ Risk Monitor (Weighted)")
    level = st.selectbox("Aggregation Level", ["Site", "Subject", "Country"])
    st.info("Input CSV columns: 'Queries', 'SAEs', 'PD_Major', 'PD_Minor' (or 'PD_Total'), 'SubjCount'")
    f_dash = st.file_uploader("Upload Dashboard (CSV)", key="cra_file")
    
    if f_dash and st.button("Analyze Risk"):
        df = pd.read_csv(f_dash)
        res = central.cra.analyze_risk(df, level)
        if isinstance(res, str): st.error(res)
        else:
            st.plotly_chart(central.cra.visualize_risk(res, level), use_container_width=True)
            st.dataframe(res, use_container_width=True)
            st.download_button("💾 Download Risk Report", res.to_csv(index=False).encode('utf-8'), "Risk_Report.csv")

# --- SITE VIEW (v1.6 Burden Analysis) ---
elif role == "🏥 Site":
    st.header("🏥 Safety Scheduler (v1.6)")
    t1, t2 = st.tabs(["🗓️ Schedule Calculator", "⚖️ Burden Analysis"])
    
    with t1:
        d = st.date_input("Start Date")
        v_name = st.text_input("Visit Name", "Visit 2")
        days = st.number_input("Target Day", 14)
        win = st.number_input("Window (+/- Days)", 2)
        
        if st.button("Calculate Compliance"):
            res = central.site.calculate_schedule(d, [{'name':v_name, 'days':days, 'window':win}])
            st.dataframe(res.style.apply(lambda x: ['background-color: #ffcccc' if "❌" in v else '' for v in x], axis=1))

    with t2:
        st.info("Calculate Burden Score based on Complexity (MRI=5, Labs=1, etc.)")
        if st.button("Run Burden Demo"):
            visits = [
                {'name':'Screening', 'procedures':['MRI', 'ECG', 'Labs', 'Vitals']},
                {'name':'Week 4', 'procedures':['Vitals', 'Dispensing']},
                {'name':'Week 12', 'procedures':['MRI', 'PK', 'Labs']}
            ]
            st.table(central.site.analyze_burden(visits))

# --- CODER VIEW (v1.6 Dictionary Validator) ---
elif role == "💊 Coder":
    st.header("💊 Coding Workbench (v1.6)")
    t1, t2, t3 = st.tabs(["Draft Query", "Coding QC", "📚 Dict Check"])
    
    with t1:
        t = st.text_input("Ambiguous Term")
        if st.button("Draft"): st.code(central.coder.draft_query(t))
        
    with t2:
        f_c = st.file_uploader("Upload Coding Log", key="cod_comp")
        if f_c and st.button("Verify Impact"):
            res = central.coder.verify_coding_impact(pd.read_csv(f_c))
            st.dataframe(res, use_container_width=True)
            
    with t3:
        f_d = st.file_uploader("Upload Terms to Validate", key="cod_dict")
        if f_d and st.button("Validate Terms"):
            res = central.coder.validate_terms(pd.read_csv(f_d))
            st.dataframe(res, use_container_width=True)

# --- WRITER VIEW (v1.6 Narrative Gen) ---
elif role == "📝 Writer":
    st.header("📝 Medical Writer (v1.6)")
    t1, t2, t3 = st.tabs(["Table Shells", "Protocol Analysis", "📖 Narrative Gen"])
    
    with t1:
        if st.button("Generate Demographics"):
            st.table(central.writer.generate_shell("Demographics"))
            
    with t2:
        f_p = st.file_uploader("Upload Protocol PDF", key="p_up")
        if f_p and st.button("Analyze Protocol"):
            st.text(central.writer.analyze_protocol_file(f_p))
            
    with t3:
        st.info("Generates Patient Narrative from Clinical Data")
        if st.button("Generate Demo Narrative"):
            demo_data = {
                'SubjectID': '101-005', 'Age': 45, 'Sex': 'Male',
                'AEs': [{'Day': 12, 'Term': 'Headache', 'Outcome': 'Resolved', 'Rel': 'Possible'}],
                'Labs': [{'Day': 12, 'Test': 'ALT', 'Val': '120 U/L'}]
            }
            st.text_area("Narrative", central.writer.write_patient_narrative(demo_data), height=400)
