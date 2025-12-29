import pandas as pd
import plotly.express as px
from datetime import datetime

class BrainCDM:
    def __init__(self):
        self.version = "CDM-1.6 (PD Edition)"

    def normalize_date(self, date_obj):
        if pd.isna(date_obj) or str(date_obj).strip() == "": return None
        for fmt in ['%Y-%m-%d', '%d-%b-%Y', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
            try: return datetime.strptime(str(date_obj).strip(), fmt).date()
            except: continue
        return None

    def detect_id(self, df):
        candidates = ['USUBJID', 'SUBJID', 'SUBJECT', 'PT', 'PATIENT', 'SUBJ_ID']
        # Ensure no duplicates in clean dict by prioritizing first occurrence
        clean = {}
        for c in df.columns:
            k = c.upper().replace("_", "").replace(" ", "")
            if k not in clean: clean[k] = c
            
        for cand in candidates:
            if cand in clean: return clean[cand]
        return df.columns[0]

    def visualize_metrics(self, issues_df, mode):
        charts = {}
        if issues_df.empty: return None
        if "Issue" in issues_df.columns:
            charts['pie'] = px.pie(issues_df, names='Issue', title=f'{mode} Breakdown', hole=0.3)
        if "Subject" in issues_df.columns:
            counts = issues_df['Subject'].value_counts().head(10).reset_index()
            counts.columns = ['Subject', 'Count']
            charts['bar'] = px.bar(counts, x='Subject', y='Count', title='Top 10 Subjects with Issues')
        return charts

    def run_recon(self, df1, df2, mode):
        # Work on copies
        df1 = df1.copy()
        if df2 is not None: df2 = df2.copy()

        # Handle Query Recon (Single DF)
        if mode == "Query_Recon": return self._run_query_recon(df1)
        
        # Handle PD Recon (Two DFs, custom logic)
        if mode == "PD_Recon": return self._run_pd_recon(df1, df2)

        # STANDARD RECON (2 DFs, Key-based)
        k1, k2 = self.detect_id(df1), self.detect_id(df2)
        df1 = df1.assign(KEY=df1[k1].astype(str).str.strip().str.upper())
        df2 = df2.assign(KEY=df2[k2].astype(str).str.strip().str.upper())
        
        merged = pd.merge(df1, df2, on='KEY', how='outer', suffixes=('_EDC', '_EXT'), indicator=True)
        issues = []

        # --- PILLAR 1: SAE (Safety vs Clinical) ---
        if mode == "SAE":
            ser = next((c for c in df1.columns if "SER" in c.upper()), "AESER")
            rel = next((c for c in df1.columns if "REL" in c.upper()), "AEREL")
            for _, r in merged[merged['_merge']=='both'].iterrows():
                if str(r.get(ser, "")).upper() not in ['Y', 'YES', 'TRUE', 'SERIOUS']:
                    issues.append({"Subject": r['KEY'], "Issue": "Seriousness Mismatch", "Detail": "Safe DB has event, EDC not Serious."})
                if rel and f"{rel}_EXT" in r:
                    if str(r.get(rel))[:3] != str(r.get(f"{rel}_EXT"))[:3]:
                        issues.append({"Subject": r['KEY'], "Issue": "Causality Conflict", "Detail": "Investigator vs Sponsor mismatch."})

        # --- PILLAR 2: LABS (Dates & QNS) ---
        elif mode == "Labs":
            d_edc = next((c for c in df1.columns if "DAT" in c.upper()), "VISITDAT")
            d_lab = next((c for c in df2.columns if "DAT" in c.upper()), "LBDAT")
            comm = next((c for c in df2.columns if "COMM" in c.upper() or "STAT" in c.upper()), None)
            res = next((c for c in df2.columns if "RES" in c.upper()), "LBORRES")
            
            for _, r in merged[merged['_merge']=='both'].iterrows():
                if pd.isna(r.get(res)) and comm and ("QNS" in str(r[comm]).upper() or "HEMOL" in str(r[comm]).upper()):
                     issues.append({"Subject": r['KEY'], "Issue": "Sample Issue", "Detail": f"Lab Rejected: {r[comm]}"})
                d1, d2 = self.normalize_date(r.get(d_edc)), self.normalize_date(r.get(d_lab))
                if d1 and d2 and abs((d2-d1).days) > 2:
                    issues.append({"Subject": r['KEY'], "Issue": "Date Mismatch", "Detail": f"Lab drawn {(d2-d1).days} days from visit."})

        # --- PILLAR 3: DEATH (Zombies & Ghosts) ---
        elif mode == "Death":
            ae_out = next((c for c in df1.columns if "OUT" in c.upper()), "AEOUT")
            ds_reas = next((c for c in df2.columns if "REAS" in c.upper()), "DSDECOD")
            fatal_map = {k: True for k, g in df1.groupby('KEY') if g[ae_out].str.contains('FATAL|DEATH', case=False, na=False).any()}
            for _, r in merged.iterrows():
                key = r['KEY']
                is_dead_ds = "DEATH" in str(r.get(ds_reas, "")).upper()
                is_dead_ae = fatal_map.get(key, False)
                if is_dead_ds and not is_dead_ae: issues.append({"Subject": key, "Issue": "Ghost Record", "Detail": "Dispo says Death, No Fatal AE."})
                if is_dead_ae and not is_dead_ds: issues.append({"Subject": key, "Issue": "Zombie Record", "Detail": "Fatal AE exists, Subject Active in Dispo."})

        # --- PILLAR 4: CODING (Homogeneity) ---
        elif mode == "Coding":
            verb = next((c for c in df1.columns if "TERM" in c.upper()), "AETERM")
            code = next((c for c in df1.columns if "LLT" in c.upper() or "CODE" in c.upper()), "AELLT")
            for term, g in df1.groupby(verb):
                codes = g[code].unique()
                clean = [c for c in codes if str(c) not in ['nan', 'None']]
                if len(clean) > 1: issues.append({"Subject": "Multiple", "Issue": "Split Coding", "Detail": f"'{term}' coded as {clean}"})

        # --- PILLAR 5: AE vs CONMED (Orphans) ---
        elif mode == "AE_ConMed":
            cm_ind = next((c for c in df2.columns if "IND" in c.upper()), "CMINDC")
            ae_term = next((c for c in df1.columns if "TERM" in c.upper()), "AETERM")
            excl = ["PROPHYLAXIS", "PREVENTION", "SUPPLEMENT"]
            unique_subjs = set(df1['KEY']).union(set(df2['KEY']))
            for s in unique_subjs:
                aes = df1[df1['KEY']==s]
                cms = df2[df2['KEY']==s]
                for _, cm in cms.iterrows():
                    ind = str(cm.get(cm_ind, "")).upper()
                    if not ind or any(e in ind for e in excl): continue
                    if not any(ind in str(a).upper() for a in aes[ae_term]):
                         issues.append({"Subject": s, "Issue": "Orphan ConMed", "Detail": f"Indication '{ind}' has no matching AE."})

        # --- PILLAR 6: MH vs CONMED (Chronic) ---
        elif mode == "MH_ConMed":
            cm_ind = next((c for c in df1.columns if "IND" in c.upper()), "CMINDC")
            mh_term = next((c for c in df2.columns if "TERM" in c.upper()), "MHTERM")
            excl = ["PROPHYLAXIS", "PREVENTION"]
            for s in set(df1['KEY']):
                cms = df1[df1['KEY']==s]
                mhs = df2[df2['KEY']==s]
                for _, cm in cms.iterrows():
                    ind = str(cm.get(cm_ind, "")).upper()
                    if not ind or any(e in ind for e in excl): continue
                    if not any(ind in str(m).upper() for m in mhs[mh_term]):
                         issues.append({"Subject": s, "Issue": "Missing History", "Detail": f"Med for '{ind}' exists, but not in Medical History."})

        return self._format_output(df1, issues)

    def _run_query_recon(self, df1):
        # --- PILLAR 7: DEEP QUERY RECONCILIATION ---
        issues = []
        stat_col = next((c for c in df1.columns if "STAT" in c.upper()), "QueryStatus")
        age_col = next((c for c in df1.columns if "AGE" in c.upper()), "DaysOpen")
        resp_col = next((c for c in df1.columns if "RESP" in c.upper() or "ANS" in c.upper()), "QueryResponse")
        rev_col = next((c for c in df1.columns if "REV" in c.upper()), None) 
        form_col = next((c for c in df1.columns if "FORM" in c.upper()), "FormOID")
        k1 = self.detect_id(df1)

        form_counts = {} 
        for _, r in df1.iterrows():
            status = str(r.get(stat_col, "")).upper()
            resp = str(r.get(resp_col, "")).upper()
            form = str(r.get(form_col, "Unknown"))
            subj = r.get(k1)
            form_counts[form] = form_counts.get(form, 0) + 1

            try:
                age = float(r.get(age_col, 0))
                if ("OPEN" in status) and age > 30: issues.append({"Subject": subj, "Issue": "Aging Query", "Detail": f"Open {age} days", "Action": "Escalate"})
            except: pass

            if "RE-OPEN" in status or (rev_col and float(r.get(rev_col, 0)) > 3):
                issues.append({"Subject": subj, "Issue": "Ping-Pong Query", "Detail": f"Re-opened multiple times", "Action": "Call Site"})

            if "ANSWER" in status and any(k in resp for k in ["WILL UPDATE", "LATER", "NOTED"]):
                issues.append({"Subject": subj, "Issue": "Lazy Answer", "Detail": f"Response: '{resp}'", "Action": "Reject"})

        if len(df1) > 0:
            for form, count in form_counts.items():
                if (count / len(df1)) > 0.25: issues.append({"Subject": "ALL", "Issue": "Form Hotspot", "Detail": f"'{form}' has >25% of queries", "Action": "Review Design"})

        return self._format_output(df1, issues)

    def _run_pd_recon(self, df1, df2):
        # --- PILLAR 8: PROTOCOL DEVIATION (PD) RECONCILIATION ---
        issues = []
        
        # Detect Columns
        pd_cat = next((c for c in df1.columns if "CAT" in c.upper() or "TERM" in c.upper()), "Category")
        pd_visit = next((c for c in df1.columns if "VISIT" in c.upper()), "Visit")
        edc_visit = next((c for c in df2.columns if "VISIT" in c.upper() or "FOLDER" in c.upper()), "Folder")
        edc_date = next((c for c in df2.columns if "DAT" in c.upper()), "VisitDate")
        
        # Normalize Keys
        k1 = self.detect_id(df1)
        k2 = self.detect_id(df2)
        
        df1 = df1.assign(KEY=df1[k1].astype(str).str.strip().str.upper())
        df2 = df2.assign(KEY=df2[k2].astype(str).str.strip().str.upper())

        # 1. The "Zombie Visit" Check (PD says Missed, EDC has Date)
        missed_pds = df1[df1[pd_cat].astype(str).str.upper().str.contains("MISS", na=False)]
        for _, pd_row in missed_pds.iterrows():
            subj = pd_row['KEY']
            visit_name = str(pd_row[pd_visit]).upper()
            edc_rows = df2[df2['KEY'] == subj]
            for _, edc_row in edc_rows.iterrows():
                edc_v_name = str(edc_row[edc_visit]).upper()
                if (visit_name in edc_v_name or edc_v_name in visit_name) and pd.notna(edc_row.get(edc_date)):
                     issues.append({"Subject": subj, "Issue": "Zombie Visit", "Detail": f"PD Log says '{visit_name}' Missed, but EDC has Date {edc_row[edc_date]}.", "Action": "Verify Data Accuracy"})
                     
        # 2. The "Silent Deviation" (EDC Out of Window, No PD)
        if "WINDOW" in [c.upper() for c in df2.columns]:
            win_col = next(c for c in df2.columns if "WINDOW" in c.upper())
            oow_visits = df2[df2[win_col].astype(str).str.upper().str.contains("OUT|FAIL|DEV", na=False)]
            for _, edc_row in oow_visits.iterrows():
                subj = edc_row['KEY']
                visit_name = str(edc_row[edc_visit]).upper()
                pd_rows = df1[df1['KEY'] == subj]
                match_found = any(visit_name in str(r[pd_visit]).upper() for _, r in pd_rows.iterrows())
                if not match_found:
                    issues.append({"Subject": subj, "Issue": "Unreported Deviation", "Detail": f"Visit '{visit_name}' OOW in EDC, missing in PD Log.", "Action": "Site to Report PD"})
        
        return self._format_output(df1, issues)

    def _format_output(self, source_df, issues):
        df_issues = pd.DataFrame(issues)
        if df_issues.empty:
            df_issues = pd.DataFrame([["✅ No Issues Found"]], columns=["Status"])
            metrics = {"Total": len(source_df), "Issues": 0, "Rate": 0.0}
        else:
            cols = ["Subject", "Issue", "Detail", "Action"]
            for c in cols: 
                if c not in df_issues.columns: df_issues[c] = "-"
            df_issues = df_issues[[c for c in cols if c in df_issues.columns]]
            metrics = {
                "Total": len(source_df), 
                "Issues": len(df_issues), 
                "Rate": round((len(df_issues)/len(source_df))*100, 1)
            }
        return df_issues, metrics
