import pandas as pd
import plotly.express as px

class BrainCRA:
    def __init__(self):
        self.version = "CRA-1.6 (Weighted PDs)"

    def analyze_risk(self, df, level):
        # 1. Grouping
        if level == 'Site': grp_col = next((c for c in df.columns if "SITE" in c.upper()), "SiteID")
        elif level == 'Subject': grp_col = next((c for c in df.columns if "SUBJ" in c.upper()), "SubjectID")
        elif level == 'Country': grp_col = next((c for c in df.columns if "CTRY" in c.upper()), "Country")
        else: return pd.DataFrame({"Error": ["Invalid grouping level"]})

        # 2. Metrics (Look for detailed PD columns)
        col_q = next((c for c in df.columns if "QUERY" in c.upper()), "Queries")
        col_sae = next((c for c in df.columns if "SAE" in c.upper()), "SAEs")
        col_pd_maj = next((c for c in df.columns if "MAJ" in c.upper()), None) # Major PDs
        col_pd_min = next((c for c in df.columns if "MIN" in c.upper()), None) # Minor PDs
        col_pd_tot = next((c for c in df.columns if "DEV" in c.upper() or "PD" in c.upper()), "PD_Total")
        col_n = next((c for c in df.columns if "COUNT" in c.upper() or "SUBJ" in c.upper()), "SubjCount")

        # 3. Aggregation
        cols = [col_q, col_sae, col_n, col_pd_maj, col_pd_min, col_pd_tot]
        valid_cols = [c for c in cols if c and c in df.columns]
        grouped = df.groupby(grp_col)[valid_cols].sum().reset_index()

        # 4. Risk Algorithm (Weighted)
        # Weights: SAE=5, Major PD=3, Queries=1, Minor PD=1
        
        q_val = grouped[col_q] if col_q in grouped else 0
        sae_val = grouped[col_sae] if col_sae in grouped else 0
        
        # Smart PD Logic: Use Major/Minor if available, else Total*2
        if col_pd_maj and col_pd_min in grouped:
            pd_score = (grouped[col_pd_maj] * 3) + (grouped[col_pd_min] * 1)
        elif col_pd_tot in grouped:
            pd_score = grouped[col_pd_tot] * 2 # Average weight assumption
        else:
            pd_score = 0

        raw_score = (q_val * 1) + (sae_val * 5) + pd_score

        # 5. Normalization (Per Subject)
        if col_n in grouped:
            # Avoid dividing by zero
            den = grouped[col_n].replace(0, 1)
            grouped['Risk Score'] = round(raw_score / den, 2)
            grouped['Risk Metric'] = "Score/Subject"
        else:
            grouped['Risk Score'] = raw_score
            grouped['Risk Metric'] = "Total Score"

        grouped['Risk Status'] = grouped['Risk Score'].apply(lambda x: "🔴 HIGH" if x > 15 else ("🟡 MEDIUM" if x > 5 else "🟢 LOW"))
        return grouped.sort_values('Risk Score', ascending=False)

    def visualize_risk(self, df, level):
        if df.empty or 'Risk Score' not in df.columns: return None
        return px.bar(df.head(20), x=df.columns[0], y='Risk Score', color='Risk Score', 
                      color_continuous_scale=['green', 'yellow', 'red'], title=f'Risk Profile by {level}')

    def generate_mvr(self, site, metrics):
        # Compatible with v1.5 text report but upgraded score display
        return f"MVR for {site}: See Risk Monitor for detailed weighted scoring."
