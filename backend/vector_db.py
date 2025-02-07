# backend/vector_db.py
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB client with new syntax
client = chromadb.PersistentClient(path="./chroma_db")

# Create sentence transformer embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)

# Get or create collection
collection = client.get_or_create_collection(
    name="travel_docs",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)