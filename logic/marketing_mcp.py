import os
import requests
import tweepy
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

# --- CONFIGURATION ---
# Keys are now fetched from Environment Variables for security
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN") # "person:123" or "organization:456"

X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

# --- TOOLS ---

@tool
def post_to_linkedin(content: str) -> str:
    """
    Posts text content to LinkedIn. Returns the status or error message.
    """
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        return "⚠️ SKIPPED LINKEDIN: No API Keys configured in environment."

    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": LINKEDIN_PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return "✅ SUCCESS: Posted to LinkedIn."
        
    except requests.exceptions.HTTPError as e:
        return f"❌ LINKEDIN ERROR: API returned {e.response.status_code}. Details: {e.response.text}"
    except Exception as e:
        return f"❌ LINKEDIN ERROR: Connection failed. {str(e)}"

@tool
def post_to_x(content: str) -> str:
    """
    Posts short text content (tweet) to X/Twitter. Returns status.
    """
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        return "⚠️ SKIPPED X: No API Keys configured."

    try:
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET
        )
        
        response = client.create_tweet(text=content)
        if response.errors:
             return f"❌ X ERROR: {response.errors}"
             
        return f"✅ SUCCESS: Posted to X. ID: {response.data['id']}"
        
    except Exception as e:
        return f"❌ X ERROR: Tweepy failed. {str(e)}"

# --- ORCHESTRATOR ---

def run_marketing_agent(audit_context: str) -> list:
    """
    Orchestrates the marketing flow.
    1. Generates content for LinkedIn and X based on audit context.
    2. Calls the respective tools.
    3. Returns a log of actions.
    """
    
    # 1. Initialize Brain
    try:
        llm = ChatVertexAI(
            model_name="gemini-1.5-pro",
            temperature=0.7, # Creative
            max_output_tokens=2048,
            location="us-central1"
        )
    except Exception as e:
        return [f"CRITICAL: Could not connect to AI Brain. {e}"]

    # 2. Bind Tools
    tools = [post_to_linkedin, post_to_x]
    llm_with_tools = llm.bind_tools(tools)
    
    # 3. Construct Prompt
    # We explicitly ask it to call BOTH tools.
    prompt = f"""
    You are the LEEVIN Marketing AI (Agent 7).
    
    CRITICAL CAMPAIGN PIVOT:
    1. 🛑 STOP promoting "Zero Draft Generation" (Feature Deprecated). Is it NOT ready.
    2. ✅ START promoting "Protocol Auditing / Stress Testing" and "RECIST 1.1 Calculation".
    
    TONE: "The Quality Assurance Firewall for your Study."
    
    INPUT CONTEXT:
    {audit_context}
    
    CAMPAIGN LOGIC:
    - IF context implies Medical Writing / Protocols:
      -> Focus on "Risk Detection", "Automated SoE Extraction", and "Chain-of-Thought Auditing".
      -> Slogan: "Don't just write. Stress test."
      
    - IF context implies Data Management / Oncology:
      -> Focus on "RECIST 1.1 Logic", "Oncology Math", and "Safety Triangulation".
      -> Slogan: "Precision Math for Precision Medicine."
    
    MISSION:
    1. Write a professional update for LinkedIn (Professional, reassuring, compliance-focused).
    2. Write a short, viral tweet for X (Tech-focused, #ClinicalTrials #Oncology #AI).
    3. Call the 'post_to_linkedin' tool with the LinkedIn content.
    4. Call the 'post_to_x' tool with the X content.
    
    CRITICAL INSTRUCTION:
    - You MUST attempt to post to BOTH platforms. 
    - Generate distinct content appropriate for each platform.
    - SIGN OFF with "Leevin Clinical".
    """
    
    messages = [HumanMessage(content=prompt)]
    
    # 4. Invoke AI
    try:
        ai_msg = llm_with_tools.invoke(messages)
    except Exception as e:
        return [f"AI Generation Failed: {e}"]

    messages.append(ai_msg)
    
    results_log = []

    # 5. execute Tool Calls
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Match tool name to function
            selected_tool = None
            if tool_name == "post_to_linkedin":
                selected_tool = post_to_linkedin
            elif tool_name == "post_to_x":
                selected_tool = post_to_x
                
            if selected_tool:
                # Execute safely
                try:
                    # Invoke variable tool (handling dictionary args)
                    result = selected_tool.invoke(tool_args)
                except Exception as e:
                    result = f"ERROR executing {tool_name}: {e}"
                
                results_log.append(result)
                
                # Update conversation history (optional, if we were continuing loop)
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    else:
        results_log.append("⚠️ No tool calls were triggered by the AI.")
        
    return results_log
