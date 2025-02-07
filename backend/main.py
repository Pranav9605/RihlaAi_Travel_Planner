from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from backend.llm_integration import generate_response
import logging

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)

class TravelQuery(BaseModel):
    destination: str
    travel_date: str
    num_days: int
    budget: str
    num_people: int
    travel_group: str
    activities: List[str]

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Travel Planner RAG API"}

@app.post("/search/")
def search(travel_query: TravelQuery):
    try:
        travel_data = travel_query.dict()
        logging.debug("Received travel data: %s", travel_data)
        response = generate_response(travel_data)
        logging.debug("Generated response: %s", response)
        return {"query": travel_data, "response": response}
    except Exception as e:
        logging.exception("Error processing travel query")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
