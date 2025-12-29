import os

class GrowthAgent:
    def __init__(self):
        self.style_path = "agent_brain/style_guide.txt"

    def draft_post(self, topic):
        style = "Professional"
        if os.path.exists(self.style_path):
            with open(self.style_path, "r") as f:
                style = f.read()
        
        print(f"🤖 GROWTH: Drafting post about '{topic}' mimicking learned style...")
        # Simulation of LLM generation
        return f"DRAFT: The industry is broken. {topic} is the fix. #ClinicalData"
