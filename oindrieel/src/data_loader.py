import json
import os


class TourismDataHandler:
    def __init__(self, filepath="data/locations.json"):
        # Automatically find the file relative to this script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(base_dir, filepath)
        self.data = self._load_data()

    def _load_data(self):
        """Loads the JSON data into memory."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found at {self.filepath}")
            return []

    def get_all_locations(self):
        """Returns raw list of dictionaries."""
        return self.data

    def filter_by_tag(self, tag):
        """
        Simple Recommendation Logic:
        Returns places that match a specific interest tag (e.g., 'History').
        """
        results = []
        for place in self.data:
            if tag.lower() in [t.lower() for t in place['tags']]:
                results.append(place['name'])
        return results

    def get_text_corpus(self):
        """
        Prepares data for the RAG Model.
        Returns a list of strings: "Name: Description"
        """
        corpus = []
        for place in self.data:
            text = f"{place['name']}: {place['description']}"
            corpus.append(text)
        return corpus


if __name__ == "__main__":
    handler = TourismDataHandler()

    print("--- Testing Tag Filter (User likes 'Adventure') ---")
    recommendations = handler.filter_by_tag("Adventure")
    print(recommendations)

    print("\n--- Testing RAG Corpus Generation ---")
    print(handler.get_text_corpus()[0])