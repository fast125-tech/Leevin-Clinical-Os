# import vertexai

def classify_document(file_obj):
    """
    Classifies a document and suggests a TMF filename.
    """
    # Mock AI Vision Classification
    # In prod: Use Gemini Pro Vision to read the first page
    
    filename = file_obj.name
    doc_type = "Unknown"
    
    if "CV" in filename or "curriculum" in filename.lower():
        doc_type = "Curriculum Vitae"
    elif "License" in filename or "medical" in filename.lower():
        doc_type = "Medical License"
    elif "IRB" in filename:
        doc_type = "IRB Approval"
        
    suggested_name = f"2025-10-12_{doc_type.replace(' ', '')}_Site101.pdf"
    
    return {
        "original_name": filename,
        "classification": doc_type,
        "confidence": "95%",
        "suggested_name": suggested_name,
        "tmf_zone": "Zone 2: Personnel"
    }
