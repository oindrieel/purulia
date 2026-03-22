import numpy as np
import re
from src.vector_engine import PuruliaRAG
from src.data_loader import TourismDataHandler
from src.trip_planner import TripPlanner


class PuruliaBrain:
    def __init__(self):
        self.rag = PuruliaRAG()
        self.data = TourismDataHandler()

        # --- THE NEW MEMORY SYSTEM ---
        self.context = {"last_places": []}

        self.intents = {
            "history_culture": "Tell me about history, culture, stories, or details of a place.",
            "recommendation": "Suggest places to visit, things to do, or attractions based on interest.",
            "trip_planner": "Plan a trip, itinerary, schedule, or route for multiple days."
        }

        print("🧠 Calibrating Intent Models...")
        self.intent_names = list(self.intents.keys())
        self.intent_vectors = self.rag.model.encode(list(self.intents.values()))

    def classify_intent(self, user_query):
        query_vec = self.rag.model.encode([user_query])
        scores = np.dot(query_vec, self.intent_vectors.T)[0]
        best_idx = np.argmax(scores)
        return self.intent_names[best_idx], scores[best_idx]

    def extract_days(self, text):
        match = re.search(r'(\d+)\s*-?\s*day', text.lower())
        if match: return int(match.group(1))
        return 1

    def extract_interests(self, text):
        text = text.lower()
        interests = []
        keywords = {
            "history": "History", "historical": "History", "ruins": "History",
            "nature": "Nature", "scenic": "Nature", "waterfall": "Nature", "hill": "Nature",
            "culture": "Culture", "mask": "Culture", "art": "Culture",
            "adventure": "Adventure", "trek": "Adventure", "photography": "Nature", "relax": "Nature"
        }
        for word, tag in keywords.items():
            if word in text and tag not in interests: interests.append(tag)
        if not interests: interests = ["Nature", "History"]
        return interests

    def process_query(self, user_text):
        print(f"\n📝 Input: '{user_text}'")
        intent, conf = self.classify_intent(user_text)
        print(f"🤔 Detected Intent: {intent.upper()} (Confidence: {conf:.2f})")

        if intent == "history_culture":
            results = self.rag.search(user_text, top_k=1)
            if results:
                return {"type": "info", "subject": results[0]['name'], "text": results[0]['description']}
            return {"error": "No relevant history found."}

        elif intent == "recommendation":
            interests = self.extract_interests(user_text)
            found_places = []
            for interest in interests:
                found_places.extend(self.data.filter_by_tag(interest))
            found_places = list(set(found_places))

            # --- SAVE TO MEMORY ---
            self.context["last_places"] = found_places

            return {"type": "recommendation", "places": found_places}

        elif intent == "trip_planner":
            planner = TripPlanner(self.data.get_all_locations())
            days = self.extract_days(user_text)
            interests = self.extract_interests(user_text)

            # --- CHECK MEMORY FOR PRONOUNS ---
            uses_context = any(word in user_text.lower() for word in ["these", "those", "them", "this"])
            specific_places = None

            if uses_context and self.context["last_places"]:
                specific_places = self.context["last_places"]
                print(f"      (Using Context Memory: {specific_places})")
                # Auto-adjust days if they have lots of places
                if "day" not in user_text.lower() and len(specific_places) >= 4:
                    days = 2

            itinerary = planner.plan_trip(days=days, interests=interests, specific_places=specific_places)
            return {"type": "plan", "itinerary": itinerary}