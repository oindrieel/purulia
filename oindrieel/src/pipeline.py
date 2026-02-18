import numpy as np
import re  # Added for smart day detection
from oindrieel.src.vector_engine import PuruliaRAG
from oindrieel.src.data_loader import TourismDataHandler
from oindrieel.src.trip_planner import TripPlanner


class PuruliaBrain:
    def __init__(self):
        self.rag = PuruliaRAG()
        self.data = TourismDataHandler()

        self.intents = {
            "history_culture": "Tell me about history, culture, stories, or details of a place.",
            "recommendation": "Suggest places to visit, things to do, or attractions based on interest.",
            "trip_planner": "Plan a trip, itinerary, schedule, or route for multiple days."
        }

        print("🧠 Calibrating Intent Models...")
        self.intent_names = list(self.intents.keys())
        self.intent_vectors = self.rag.model.encode(list(self.intents.values()))

    def classify_intent(self, user_query):
        """Decides what the user wants."""
        query_vec = self.rag.model.encode([user_query])
        scores = np.dot(query_vec, self.intent_vectors.T)[0]
        best_idx = np.argmax(scores)
        best_intent = self.intent_names[best_idx]
        confidence = scores[best_idx]
        return best_intent, confidence

    def extract_days(self, text):
        """Finds '3 days', '2 day', '5-day' in text using Regex."""
        match = re.search(r'(\d+)\s*-?\s*day', text.lower())
        if match:
            return int(match.group(1))
        return 1  # Default

    def extract_interests(self, text):
        """Scans text for keywords to build an interest list."""
        text = text.lower()
        interests = []
        keywords = {
            "history": "History", "historical": "History", "ancient": "History", "ruins": "History",
            "nature": "Nature", "scenic": "Nature", "waterfall": "Nature", "hill": "Nature",
            "culture": "Culture", "mask": "Culture", "dance": "Culture", "art": "Culture",
            "adventure": "Adventure", "trek": "Adventure", "hiking": "Adventure",
            "photography": "Nature", "photo": "Nature", "camera": "Nature",
            "relax": "Nature", "chill": "Nature"
        }

        for word, tag in keywords.items():
            if word in text:
                if tag not in interests:
                    interests.append(tag)

        if not interests:
            interests = ["Nature", "History"]

        return interests

    def process_query(self, user_text):
        print(f"\n📝 Input: '{user_text}'")

        intent, conf = self.classify_intent(user_text)
        print(f"🤔 Detected Intent: {intent.upper()} (Confidence: {conf:.2f})")

        response = {}

        if intent == "history_culture":
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
            print("   -> Routing to Recommendation Engine...")
            interests = self.extract_interests(user_text)

            found_places = []
            for interest in interests:
                found_places.extend(self.data.filter_by_tag(interest))

            found_places = list(set(found_places))

            response = {
                "type": "recommendation",
                "places": found_places
            }

        elif intent == "trip_planner":
            print("   -> Routing to Trip Planner...")

            planner = TripPlanner(self.data.get_all_locations())

            days = self.extract_days(user_text)
            interests = self.extract_interests(user_text)

            print(f"      (Extracted: {days} days, Interests: {interests})")

            itinerary = planner.plan_trip(days=days, interests=interests)

            response = {
                "type": "plan",
                "itinerary": itinerary
            }

        return response


if __name__ == "__main__":
    brain = PuruliaBrain()
    brain.process_query("Plan a 3 day trip for scenic places")