from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import spacy
import traceback
# import google.generativeai as genai
import openai
# Import your LLM integration function and image scraper module.
from backend.llm_integration import generate_response
from backend.duckduckgo_scraper import scrape_duckduckgo_image

# Configure basic logging.
logging.basicConfig(level=logging.DEBUG)

# Configure the Gemini client with API key.
# from backend.config import OPENAI_API_KEY
# genai.configure(api_key=OPENAI_API_KEY)


from backend.config import OPENAI_API_KEY


# Pydantic model for travel query.
class TravelQuery(BaseModel):
    destination: str
    travel_date: str
    num_days: int
    budget: str
    num_people: int
    travel_group: str
    activities: List[str]
    additional_comments: str = ""

# Load spaCy's English model for NER.
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords (e.g., place names) from text using spaCy NER.
    Extracts entities labeled as GPE, LOC, or ORG.
    """
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "ORG")]
    return list(set(keywords))

def dynamic_format_itinerary(plan_text: str, augmented_items: List[Dict[str, str]]) -> str:
    """
    Dynamically format the itinerary text into Markdown.
    Splits text into lines and appends an image snippet with hyperlink for any keyword found,
    ensuring each keyword is rendered only once.
    """
    lines = plan_text.splitlines()
    formatted_lines = []
    rendered_keywords = set()

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        formatted_lines.append(stripped_line)
        for item in augmented_items:
            keyword = item["keyword"].lower()
            if keyword in stripped_line.lower() and keyword not in rendered_keywords:
                snippet = (
                    f"\n![{item['keyword']}]({item['image_url']})\n"
                    f"[More Info]({item['more_info_link']})"
                )
                formatted_lines.append(snippet)
                rendered_keywords.add(keyword)

    return "\n\n".join(formatted_lines)

app = FastAPI(title="RihlaAi Travel & Weather Planner API")

@app.get("/")
def home():
    return {"message": "Welcome to Travel Planner RAG API"}

@app.post("/search/")
def search(travel_query: TravelQuery):
    try:
        travel_data = travel_query.dict()
        logging.debug("Received travel data: %s", travel_data)

        itinerary_text = generate_response(travel_data)
        logging.debug("Generated itinerary text: %s", itinerary_text)

        extracted_keywords = extract_keywords(itinerary_text)
        logging.debug("Extracted keywords (raw): %s", extracted_keywords)

        destination_lower = travel_data.get("destination", "").lower()
        filtered_keywords = [kw for kw in extracted_keywords if kw.lower() != destination_lower]
        logging.debug("Filtered keywords (excluding destination): %s", filtered_keywords)

        augmented_items = []
        for keyword in filtered_keywords:
            image_url = scrape_duckduckgo_image(keyword)
            more_info_link = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            augmented_items.append({
                "keyword": keyword,
                "image_url": image_url,
                "more_info_link": more_info_link
            })
        logging.debug("Raw augmented items: %s", augmented_items)

        unique_augmented = {}
        for item in augmented_items:
            key = item["keyword"].lower()
            if key not in unique_augmented:
                unique_augmented[key] = item
        augmented_items = list(unique_augmented.values())
        logging.debug("Deduplicated augmented items: %s", augmented_items)

        rendered_html = dynamic_format_itinerary(itinerary_text, augmented_items)
        logging.debug("Rendered HTML output: %s", rendered_html)

        return {
            "query": travel_data,
            "itinerary": itinerary_text,
            "augmented": augmented_items,
            "rendered_output": rendered_html
        }
    except Exception as e:
        logging.exception("Error processing travel query")
        raise HTTPException(status_code=500, detail=str(e))

# Include the weather forecast router.
from backend.weather_forecast import router as weather_router
app.include_router(weather_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
