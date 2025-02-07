from backend.vector_db import collection  # Import the Chroma DB collection
from sentence_transformers import SentenceTransformer

from backend.embedding import embedding_model  # Use a suitable model


def retrieve_relevant_docs(query: str, top_k: int = 5):
   
    """Retrieves the top_k relevant documents based on the query."""
    # Convert the query to embeddings
    query_embedding = embedding_model.encode(query).tolist()
    
    # Perform the retrieval from the collection
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    return results['documents']  # Adjust based on the data you want to retrieve