import time
import schedule
from agents.graph_learner import GraphLearner
from agents.marketing_agent import GrowthAgent

def job_night_school():
    print("🌙 NIGHT SCHOOL: Graph Learner Active")
    learner = GraphLearner()
    learner.learn_topic("Tramadol") # Example topic
    learner.close()

def job_marketing():
    agent = GrowthAgent()
    print(agent.draft_post("GraphRAG in CDM"))

print("🚀 LEEVIN OS v2.0 STARTED")
print("   - GraphRAG: Active")
print("   - NLP Engine: Active")
print("   - Omni-CDM: Active")

schedule.every().day.at("02:00").do(job_night_school)
schedule.every().day.at("09:00").do(job_marketing)

while True:
    schedule.run_pending()
    time.sleep(1)
