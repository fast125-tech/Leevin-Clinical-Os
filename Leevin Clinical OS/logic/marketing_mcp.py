import requests
import json

# Configuration
LINKEDIN_ORG_ID = "110332693"
LINKEDIN_BASE_URL = "https://api.linkedin.com/v2"
# In production, fetch this from a secure secret manager
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN" 

def post_to_linkedin(text, media_url=None):
    """
    Posts content to the Company Page (Organization).
    """
    url = f"{LINKEDIN_BASE_URL}/ugcPosts"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    author = f"urn:li:organization:{LINKEDIN_ORG_ID}"
    
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # Mocking the API call for now to avoid errors without a real token
    # response = requests.post(url, headers=headers, json=payload)
    # return response.json()
    
    return {"status": "success", "mock_response": "Posted to LinkedIn Page 110332693"}

def generate_campaign_posts():
    """
    Generates the 'Operation Breadcrumbs' 3-Day Campaign.
    """
    campaign = {
        "Day 1": {
            "Target": "The Medical Writer",
            "Theme": "The Zero Draft Revolution",
            "Content": (
                "POLL: How much time do you spend formatting SoE tables?\n\n"
                "A) < 1 hour\n"
                "B) 1-5 hours\n"
                "C) Too much (It's painful)\n\n"
                "KAIROS extracts SoE tables from PDF to Excel in 5 seconds. "
                "See the proof on our page. #ClinicalResearch #MedicalWriting #Automation"
            )
        },
        "Day 2": {
            "Target": "The Data Manager",
            "Theme": "VLOOKUP is Dead",
            "Content": (
                "HOT TAKE: If you are still using Excel VLOOKUP to reconcile Lab Data vs EDC, "
                "you are working too hard.\n\n"
                "There is a file-based AI for that. It fuzzy matches subjects and flags mismatches instantly.\n\n"
                "Comment 'RECON' for a free demo link. #ClinicalDataManagement #NoMoreVLOOKUP #AI"
            )
        },
        "Day 3": {
            "Target": "The Site Coordinator",
            "Theme": "Inbox Zero for Research",
            "Content": (
                "Story time: A CRC missed a critical SAE email because it was buried in a thread of 50 replies.\n\n"
                "It happens. But it shouldn't.\n\n"
                "Our Mailroom module stitches email threads by Patient ID automatically. "
                "Never miss a safety alert again.\n\n"
                "#ClinicalTrials #SiteCoordinator #PatientSafety"
            )
        }
    }
    return campaign
