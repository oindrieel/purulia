import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from oindrieel.src.data_loader import TourismDataHandler


class PuruliaRAG:
    def __init__(self):
        # 1. Define the specific folder for models
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models")

        print(f"⏳ Loading AI Model into '{model_path}'...")

        # 2. Load model with 'cache_folder' pointing to your directory
        self.model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=model_path)

        # Connect to your Data Loader
        self.data_handler = TourismDataHandler()
        self.corpus = self.data_handler.get_text_corpus()
        self.raw_data = self.data_handler.get_all_locations()

        # Internal storage for the vector index
        self.index = None
        self._build_index()

    def _build_index(self):
        """Converts text corpus into vectors and stores them in FAISS."""
        if not self.corpus:
            print("⚠️ Warning: Corpus is empty.")
            return

        print(f"📊 Encoding {len(self.corpus)} locations into vectors...")
        embeddings = self.model.encode(self.corpus)

        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)
        print("✅ Vector Index Built Successfully!")

    def search(self, user_query, top_k=2):
        query_vector = self.model.encode([user_query])
        query_vector = np.array(query_vector).astype('float32')

        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for i in range(top_k):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    "name": self.raw_data[idx]['name'],
                    "match_score": float(distances[0][i]),
                    "description": self.raw_data[idx]['description']
                })
        return results


if __name__ == "__main__":
    rag = PuruliaRAG()

    query = "I want to see traditional dance masks"
    print(f"\n🔎 User Query: '{query}'")

    hits = rag.search(query)

    for hit in hits:
        print(f"   🎯 Found: {hit['name']}")
        print(f"      Context: {hit['description'][:100]}...")