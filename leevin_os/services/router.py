
import os
import pandas as pd
import pdfplumber

class HybridRouter:
    """
    The Dispatcher: Identifies input type and routes to the correct Brain.
    """
    
    @staticmethod
    def identify_and_read(file_obj):
        """
        Input: Streamlit UploadedFile
        Output: (Type_String, Content_Object)
        """
        filename = file_obj.name.lower()
        
        try:
            if filename.endswith('.csv'):
                # Route to Brain 1 (Data)
                df = pd.read_csv(file_obj)
                return "DATAFRAME", df
            
            elif filename.endswith('.xlsx'):
                # Route to Brain 1 (Data)
                df = pd.read_excel(file_obj)
                return "DATAFRAME", df
                
            elif filename.endswith('.pdf'):
                # Route to Brain 3 (Text Analysis)
                text = ""
                with pdfplumber.open(file_obj) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                return "TEXT", text
                
            else:
                return "UNKNOWN", None
                
        except Exception as e:
            return "ERROR", str(e)
