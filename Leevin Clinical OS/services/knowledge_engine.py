# from google.cloud import discoveryengine_v1 as discoveryengine

def search_global(query, project_id):
    """
    Searches across all project documents using Vertex AI Search.
    """
    # client = discoveryengine.SearchServiceClient()
    # serving_config = client.serving_config_path(
    #     project="syran-clinical",
    #     location="global",
    #     data_store="kairos-docs",
    #     serving_config="default_config",
    # )
    
    # request = discoveryengine.SearchRequest(
    #     serving_config=serving_config,
    #     query=query,
    #     page_size=5,
    #     filter=f"project_id: ANY(\"{project_id}\")"
    # )
    # response = client.search(request)
    
    # Mock Response
    return [
        {"title": "Protocol V1.pdf", "snippet": "...hemoglobin levels must be checked..."},
        {"title": "Lab_Manual.pdf", "snippet": "...hemoglobin analysis procedure..."}
    ]
