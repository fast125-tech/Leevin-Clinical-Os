import tweepy
import requests
from services.cloud_ops import get_secrets

def post_to_linkedin(content: str):
    """
    Post to LinkedIn via API.
    """
    try:
        access_token = get_secrets("LINKEDIN_ACCESS_TOKEN")
        author_urn = get_secrets("LINKEDIN_AUTHOR_URN")
        
        if not access_token or not author_urn:
            return False

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": author_urn,
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
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to post to LinkedIn: {e}")
        return False

def post_to_x(content: str):
    """
    Post to X (Twitter) via Tweepy.
    """
    try:
        bearer_token = get_secrets("TWITTER_BEARER_TOKEN")
        consumer_key = get_secrets("TWITTER_CONSUMER_KEY")
        consumer_secret = get_secrets("TWITTER_CONSUMER_SECRET")
        access_token = get_secrets("TWITTER_ACCESS_TOKEN")
        access_token_secret = get_secrets("TWITTER_ACCESS_TOKEN_SECRET")
        
        if not consumer_key:
            return False

        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        client.create_tweet(text=content)
        return True
    except Exception as e:
        print(f"Failed to post to X: {e}")
        return False
