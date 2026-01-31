import numpy as np
from src.vector_engine import PuruliaRAG
from src.data_loader import TourismDataHandler
from src.trip_planner import TripPlanner

class PuruliaBrain:
    def __init__(self):
        # 1. Initialize your RAG engine (which holds the AI model)
        self.rag = PuruliaRAG()
        self.data = TourismDataHandler()

        # 2. Define your "Intents" (The categories the AI understands)
        self.intents = {
            "history_culture": "Tell me about history, culture, stories, or details of a place.",
            "recommendation": "Suggest places to visit, things to do, or attractions based on interest.",
            "trip_planner": "Plan a trip, itinerary, schedule, or route for multiple days."
        }

        # 3. Pre-calculate Intent Vectors (Optimization)
        # We use the existing model to understand what these intents mean
        print("🧠 Calibrating Intent Models...")
        self.intent_names = list(self.intents.keys())
        self.intent_vectors = self.rag.model.encode(list(self.intents.values()))

    def classify_intent(self, user_query):
        """
        Decides what the user wants by comparing their query to the Intent definitions.
        """
        # Vectorize user query
        query_vec = self.rag.model.encode([user_query])

        # Calculate similarity (Dot Product)
        scores = np.dot(query_vec, self.intent_vectors.T)[0]

        # Get the highest score
        best_idx = np.argmax(scores)
        best_intent = self.intent_names[best_idx]
        confidence = scores[best_idx]

        return best_intent, confidence

    def process_query(self, user_text):
        print(f"\n📝 Input: '{user_text}'")

        # Step A: Classify
        intent, conf = self.classify_intent(user_text)
        print(f"🤔 Detected Intent: {intent.upper()} (Confidence: {conf:.2f})")

        response = {}

        # Step B: Route to the right tool
        if intent == "history_culture":
            # Call RAG
            print("   -> Routing to RAG Engine...")
            results = self.rag.search(user_text, top_k=1)
            if results:
                best_match = results[0]
                response = {
                    "type": "info",
                    "subject": best_match['name'],
                    "text": best_match['description']
                }
            else:
                response = {"error": "No relevant history found."}

        elif intent == "recommendation":
            # Call Tag Filter (Simple Logic for now)
            print("   -> Routing to Recommendation Engine...")
            # Extract basic keywords manually for this week (We will upgrade this later)
            found_places = []
            if "adventure" in user_text.lower():
                found_places = self.data.filter_by_tag("Adventure")
            elif "history" in user_text.lower():
                found_places = self.data.filter_by_tag("History")
            else:
                found_places = ["Ayodhya Hills", "Charida Village"]  # Default

            response = {
                "type": "recommendation",
                "places": found_places
            }


        elif intent == "trip_planner":

            print("   -> Routing to Trip Planner...")

            # 1. Initialize Planner with raw data

            planner = TripPlanner(self.data.get_all_locations())

            # 2. Extract constraints (Basic logic for now)

            # Default to 2 days if not specified

            days = 2 if "2 day" in user_text or "two day" in user_text else 1

            # Default interests if none detected

            interests = ["nature", "history"]

            if "adventure" in user_text: interests = ["adventure"]

            # 3. Generate Plan

            itinerary = planner.plan_trip(days=days, interests=interests)

            response = {

                "type": "plan",

                "itinerary": itinerary

            }

        return response


# --- Test Block ---
if __name__ == "__main__":
    brain = PuruliaBrain()

    # Test 1: History Request
    brain.process_query("What is the story behind the masks?")

    # Test 2: Recommendation Request
    brain.process_query("I like adventure and trekking.")

    # Test 3: Planning Request
    brain.process_query("Make a 2 day plan for me.")