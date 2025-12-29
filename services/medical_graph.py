import networkx as nx

class MedicalGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.load_initial_knowledge()

    def load_initial_knowledge(self):
        # Base ontology - expands as it learns
        self.add_relationship("Advil", "is_brand_of", "Ibuprofen")
        self.add_relationship("Ibuprofen", "is_class", "NSAID")
        self.add_relationship("NSAID", "contraindicated_in", "Kidney Disease")
        self.add_relationship("Bleeding", "is_adverse_event_of", "Warfarin")

    def add_relationship(self, subject, relation, object_):
        self.G.add_edge(subject, object_, relation=relation)

    def find_connection(self, start_term, end_term):
        try:
            path = nx.shortest_path(self.G, source=start_term, target=end_term)
            explanation = f"{start_term}"
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                rel = self.G[u][v]['relation']
                explanation += f" --({rel})--> {v}"
            return explanation
        except nx.NetworkXNoPath:
            return None
