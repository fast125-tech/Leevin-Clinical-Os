import feedparser
from logic.agent_logic import llm

class RegulatoryRadar:
    def __init__(self):
        # Mock RSS Feeds or Real URLs if internet available
        self.rss_feeds = {
            "FDA": "https://www.fda.gov/about-fda/contact-fda/stay-connected/rss-feeds/drug-safety-podcasts/rss.xml", # Example
            "EMA": "https://www.ema.europa.eu/en/rss/news.xml"
        }
        
        # Mocking 2025 Guidances for the MVP context
        self.mock_guidances = [
            {"title": "Decentralized Clinical Trials 2025 Final Guidance", "summary": "Requires explicit remote consent workflows and home health safety monitoring."},
            {"title": "AI in Pharmacovigilance 2025", "summary": "Mandates 'Human-in-the-Loop' for all AI-generated safety signals."},
            {"title": "Diversity Action Plans 2025", "summary": "Phase 3 trials must have diverse enrollment targets pre-specified."}
        ]

    def check_compliance(self, protocol_text):
        """
        Checks protocol text against the latest (Mock) Guidances.
        """
        if not llm: return []
        
        # 1. Fetch Feeds (Mocked for stability)
        # In real prod: feed = feedparser.parse(url)
        
        context_str = "\n".join([f"- {g['title']}: {g['summary']}" for g in self.mock_guidances])
        
        template = f"""
        You are a Regulatory Affairs Officer.
        Compare this Protocol Text against these NEW 2025 Guidelines.
        
        GUIDELINES:
        {context_str}
        
        PROTOCOL SNIPPET:
        {protocol_text[:10000]}
        
        TASK:
        If the protocol fails to mention requirements (e.g. Remote Consent for DCT, Diversity Plan), flag it.
        
        OUTPUT FORMAT:
        - Alert: [Guideline Title] - [Issue Description]
        """
        
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        
        try:
            response = chain.invoke({}).content
            alerts = []
            for line in response.split('\n'):
                if "Alert:" in line or "-" in line:
                    alerts.append(line.strip())
            return alerts
        except:
             return ["⚠️ System Error: Could not run Regulatory Scan."]
