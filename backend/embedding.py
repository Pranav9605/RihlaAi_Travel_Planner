# backend/embedding.py
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # Or your preferred model
embedding_model = SentenceTransformer(MODEL_NAME)
