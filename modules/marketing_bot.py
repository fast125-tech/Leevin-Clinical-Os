import random
import datetime
import streamlit as st
from logic.marketing_mcp import post_to_linkedin, post_to_x

class MarketingBot:
    def __init__(self):
        self.campaigns = [
            {
                "name": "CAMPAIGN A: The Medical Writer ($49)",
                "target": "Medical Writers",
                "price": "$49",
                "prompt": "Write a LinkedIn Poll targeting Medical Writers. Ask: 'If you could pay $49 to automate one task instantly, which one?' Options: 1. Zero-Drafting 2. SoE Formatting 3. Logic Audit 4. I wouldn't pay. Hook: 'The Blank Page is expensive.'"
            },
            {
                "name": "CAMPAIGN B: The Data Manager ($99)",
                "target": "Data Managers",
                "price": "$99",
                "prompt": "Write a LinkedIn Poll targeting Data Managers. Ask: 'We are building an Excel Killer. Which feature makes $99/mo a no-brainer?' Options: 1. Auto-Query Writing 2. Lab Recon 3. UAT Scripts 4. $99 is too high. Hook: 'Stop working weekends.'"
            },
            {
                "name": "CAMPAIGN C: The Magic Wand ($199)",
                "target": "Clinical Ops Leaders",
                "price": "$199",
                "prompt": "Write a LinkedIn Poll targeting Clinical Ops Leaders. Ask: 'I have a magic wand. I can delete one task for a flat fee of $199. What do you choose?' Options: 1. Visual SDV 2. TMF Filing 3. Back-Translation 4. Keep my money. Hook: 'Time vs Money.'"
            }
        ]

    def get_todays_strategy(self):
        """
        Selects a campaign based on an 8-hour rotation window.
        """
        now = datetime.datetime.now()
        hour = now.hour
        
        # 0-8: Campaign A, 8-16: Campaign B, 16-24: Campaign C
        if 0 <= hour < 8:
            return self.campaigns[0]
        elif 8 <= hour < 16:
            return self.campaigns[1]
        else:
            return self.campaigns[2]

    def run_auto_scheduler(self):
        """
        Executes the selected campaign.
        """
        campaign = self.get_todays_strategy()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[CAMPAIGN EXECUTED]: {campaign['name']} - {timestamp}")
        
        # In a real scenario, we would generate content using Gemini here
        # For validation, we will just post the "Prompt" or a mock generated version
        
        # Mocking Generation (since we want to validate the logic flow)
        generated_content = f"📢 POLL: {campaign['target']}!\n\n{campaign['prompt']}\n\nVote below! #ClinicalTrials #{campaign['price']}"
        
        # Execute Posts
        # In Autonomous Mode, we might want to actually post, but to be safe we print/log
        # or use the tools if configured.
        
        # self.post_to_linkedin(generated_content) # Uncomment to go live
        # self.post_to_x(generated_content)        # Uncomment to go live
        
        return {
            "status": "Executed",
            "campaign": campaign['name'],
            "content": generated_content,
            "time": timestamp
        }
