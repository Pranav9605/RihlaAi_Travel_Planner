import json
from typing import List, Dict

DATA_PATH = "/Users/pranavpadmanabhan/Documents/Project/RAG_FastApi/travel-planner-rag/data/combined_rag_data.json"

def load_data() -> List[Dict]:
    """Loads combined hotel, restaurant, and entertainment data."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["hotels"] + data["restaurants"] + data["entertainment"]  # Merge all data types

if __name__ == "__main__":
    data = load_data()
    print(f"Loaded {len(data)} records.")
