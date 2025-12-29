import pandas as pd
import streamlit as st
from langchain_core.prompts import PromptTemplate
from logic.agent_logic import llm, ai_retry

class EditCheckExecutor:
    def __init__(self):
        self.llm = llm

    @ai_retry
    def translate_to_query(self, rule_text, columns):
        """
        Translates a natural language rule into a Pandas .query() string.
        """
        if not self.llm: return None

        template = """
        Role: Python Data Scientist.
        Task: Convert this Clinical Data Validation Rule into a Pandas `.query()` string.
        
        The query should select rows that FAIL the check (Rows that match the error condition).
        
        Rule: "{rule}"
        Available Columns: {columns}
        
        Examples:
        - Rule: "Age must be greater than 18" -> Query: "Age <= 18" (Finds the failures)
        - Rule: "If Gender is Male, Pregnancy must be Null" -> Query: "Gender == 'Male' and Pregnancy.notnull()"
        
        OUTPUT ONLY THE QUERY STRING. NO MARKDOWN. NO QUOTES.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        return chain.invoke({"rule": rule_text, "columns": columns}).content.strip().strip('"').strip("'")

    def run_spec_based_checks(self, data_file, spec_file):
        """
        Executes checks from spec_file (Excel) against data_file (CSV).
        Returns a DataFrame of Discrepancies.
        """
        try:
            # 1. Load Data
            df_data = pd.read_csv(data_file)
            df_spec = pd.read_excel(spec_file)
            
            # Validate Spec Structure
            required_cols = ["CheckID", "Description", "Logic_Rule"]
            if not all(col in df_spec.columns for col in required_cols):
                return pd.DataFrame({"Error": [f"Spec file missing required columns: {required_cols}"]})

            discrepancies = []
            cols_str = ", ".join(df_data.columns.tolist())

            # 2. Iterate Rules
            total_checks = len(df_spec)
            
            # Initial Status Feedback (if running in streamlit context we can yield, 
            # but for simplicity we return data and let UI handle spinners)
            
            for index, row in df_spec.iterrows():
                check_id = row['CheckID']
                desc = row['Description']
                logic = row['Logic_Rule']
                
                # 3. Translate Logic
                try:
                    query = self.translate_to_query(logic, cols_str)
                    
                    if not query or "Error" in query:
                         discrepancies.append({
                            "CheckID": check_id,
                            "Status": "Logic Error",
                            "Message": "AI could not generate query."
                        })
                         continue

                    # 4. Execute (Sandboxed)
                    failures = df_data.query(query)
                    
                    if not failures.empty:
                        for _, fail_row in failures.iterrows():
                            # Create a snippet of the data
                            row_dump = fail_row.to_dict()
                            # Try to identify a Subject ID if possible
                            subj = fail_row.get('SubjectID', fail_row.get('SUBJID', 'Unknown'))
                            
                            discrepancies.append({
                                "SubjectID": subj,
                                "CheckID": check_id,
                                "Description": desc,
                                "Logic": logic,
                                "Status": "Fail",
                                "Data_Snippet": str(row_dump)
                            })
                            
                except Exception as e:
                    discrepancies.append({
                        "CheckID": check_id,
                        "Status": "Execution Error",
                        "Message": str(e)
                    })

            return pd.DataFrame(discrepancies)

        except Exception as e:
             return pd.DataFrame({"Error": [f"Critical Engine Failure: {str(e)}"]})
