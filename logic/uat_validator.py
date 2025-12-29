import pandas as pd
import datetime
import plotly.express as px
from fpdf import FPDF
import os

# --- VALIDATION LOGIC ---

def validate_uat_results(expected_df, actual_df):
    """
    Compares the Synthetic Data (Plan) vs the EDC Export (Reality).
    Returns a DataFrame with Pass/Fail status.
    """
    validation_log = []
    
    # Normalize Columns (Upper case)
    expected_df.columns = [c.upper() for c in expected_df.columns]
    actual_df.columns = [c.upper() for c in actual_df.columns]
    
    # Identify Subject Column
    subj_col = 'SUBJECTID' if 'SUBJECTID' in expected_df.columns else 'SUBJECT'
    
    # Iterate through Expected Data
    for index, row in expected_df.iterrows():
        subj = str(row.get(subj_col, '')).strip()
        field = str(row.get('FIELD', '')).strip()
        expected_val = str(row.get('VALUE', '')).strip()
        scenario = str(row.get('SCENARIO', 'Unknown')) # From new UAT Engine
        
        # Find match in Actual
        match = actual_df[
            (actual_df[subj_col] == subj) & 
            (actual_df['FIELD'] == field)
        ]
        
        status = "FAIL"
        note = ""
        actual_val = "N/A"
        
        if match.empty:
            actual_val = "N/A"
            # Negative Test Logic: If we planned a failure, and it's missing in export (blocked), that's a PASS.
            if _is_negative_test_pass(expected_val, "", scenario):
                 status = "PASS"
                 note = "Negative Test Success (Blocked/Not Saved)"
            else:
                 status = "MISSING"
                 note = "Record missing in EDC Export"
        else:
            actual_val = str(match.iloc[0]['VALUE']).strip()
            if actual_val.lower() == 'nan': actual_val = ""
            
            if actual_val == expected_val:
                status = "PASS"
                note = "Exact Match"
            elif _is_negative_test_pass(expected_val, actual_val, scenario):
                status = "PASS"
                note = "Negative Test Success (Query/Blocked)"
            else:
                status = "FAIL"
                note = f"Mismatch: Exp '{expected_val}' vs Act '{actual_val}'"
        
        validation_log.append({
            "Test_ID": f"TC_{index}",
            "Subject": subj,
            "Field": field,
            "Expected": expected_val,
            "Actual": actual_val,
            "Scenario": scenario,
            "Status": status,
            "Notes": note
        })
        
    return pd.DataFrame(validation_log)

def _is_negative_test_pass(val_exp, val_act, scenario):
    """
    Passes if Scenario is Failure/Boundary AND Actual is Empty.
    """
    if "Failure" in scenario or "Boundary" in scenario or "Negative" in scenario:
        # If Actual is empty, it means EDC prevented the save -> PASS
        if val_act == "" or val_act.lower() == "nan" or val_act == "None":
            return True
    return False

def generate_metrics_chart(validation_df):
    """
    Creates a visual summary for the report using Plotly.
    """
    if validation_df.empty: return None
    counts = validation_df['Status'].value_counts().reset_index()
    counts.columns = ['Status', 'Count']
    color_map = {'PASS': '#28a745', 'FAIL': '#dc3545', 'MISSING': '#ffc107'}
    fig = px.pie(counts, values='Count', names='Status', title='UAT Execution Summary', color='Status', color_discrete_map=color_map, hole=0.4)
    fig.update_layout(title_font_size=24, title_x=0.5)
    return fig

# --- PDF REPORTING ---

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Leevin Clinical OS | UAT Validation Certificate', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_validation_pdf(df_results):
    """
    Generates a PDF Certificate from the validation results.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "Certificate of Validation", 0, 1, 'C')
    pdf.set_device_color(30, 58, 138) # Royal Blue
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Meta Info
    pdf.set_font("Arial", '', 12)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 8, f"Date: {timestamp}", 0, 1)
    pdf.cell(0, 8, f"System: EDC (Advanced Validation)", 0, 1)
    pdf.cell(0, 8, f"Scope: Automated Logic Verification (Clean/Boundary/Failure)", 0, 1)
    pdf.ln(10)
    
    # Metrics
    total = len(df_results)
    passed = len(df_results[df_results['Status'] == "PASS"])
    failed = total - passed
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Execution Summary:", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(40, 8, "Total Tests:", 0, 0)
    pdf.cell(0, 8, str(total), 0, 1)
    pdf.cell(40, 8, "Passed:", 0, 0)
    pdf.cell(0, 8, str(passed), 0, 1)
    pdf.cell(40, 8, "Failed:", 0, 0)
    pdf.cell(0, 8, str(failed), 0, 1)
    pdf.cell(40, 8, "Pass Rate:", 0, 0)
    pdf.cell(0, 8, f"{pass_rate}%", 0, 1)
    pdf.ln(10)
    
    # Verdict Stamp
    pdf.set_font("Arial", 'B', 24)
    if pass_rate == 100:
        pdf.set_text_color(0, 128, 0) # Green
        pdf.cell(0, 15, "VALIDATED", 0, 1, 'C')
    else:
        pdf.set_text_color(220, 53, 69) # Red
        pdf.cell(0, 15, "ISSUES FOUND", 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.ln(10)
    
    # Detailed Failures (if any)
    if failed > 0:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Failure Log (Top 10):", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        failures = df_results[df_results['Status'] != "PASS"].head(10)
        
        # Simple table
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(20, 8, "Subj", 1, 0, 'C', True)
        pdf.cell(30, 8, "Field", 1, 0, 'C', True)
        pdf.cell(70, 8, "Issue", 1, 0, 'C', True)
        pdf.cell(70, 8, "Expected", 1, 1, 'C', True)
        
        for _, row in failures.iterrows():
            pdf.cell(20, 8, str(row['Subject']), 1)
            pdf.cell(30, 8, str(row['Field']), 1)
            pdf.cell(70, 8, str(row['Notes'])[:35], 1)
            pdf.cell(70, 8, str(row['Expected'])[:35], 1)
            pdf.ln()
            
    # Output file
    out_file = "UAT_Certificate_Advanced.pdf"
    pdf.output(out_file)
    return out_file
