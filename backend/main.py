from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import spacy
from backend.weather_forecast import router as weather_router
# Import your LLM integration function and image scraper module.
from backend.llm_integration import generate_response
from backend.duckduckgo_scraper import scrape_duckduckgo_image

# Configure basic logging.
logging.basicConfig(level=logging.DEBUG)

# Pydantic model for the travel query input.
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
    Here we extract entities labeled as GPE, LOC, or ORG.
    """
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "ORG")]
    return list(set(keywords))

def dynamic_format_itinerary(plan_text: str, augmented_items: List[Dict[str, str]]) -> str:
    """
    Dynamically format the itinerary text into Markdown.
    The function splits the text into lines and, for each line,
    appends an image snippet and hyperlink if a keyword is found and not already rendered.
    """
    # Split the itinerary text into lines for better segmentation.
    lines = plan_text.splitlines()
    formatted_lines = []
    rendered_keywords = set()  # Track keywords already rendered.
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        # Add the original line.
        formatted_lines.append(stripped_line)
        
        # For each augmented item, if its keyword appears and hasn't been rendered, append its snippet.
        for item in augmented_items:
            keyword = item["keyword"].lower()
            if keyword in stripped_line.lower() and keyword not in rendered_keywords:
                snippet = (
                    f"\n![{item['keyword']}]({item['image_url']})\n"
                    f"[More Info]({item['more_info_link']})"
                )
                formatted_lines.append(snippet)
                rendered_keywords.add(keyword)
    
    # Join with double newlines for clear Markdown separation.
    return "\n\n".join(formatted_lines)

app = FastAPI()
app.include_router(weather_router)

@app.get("/")
def home():
    return {"message": "Welcome to Travel Planner RAG API"}

@app.post("/search/")
def search(travel_query: TravelQuery):
    try:
        travel_data = travel_query.dict()
        logging.debug("Received travel data: %s", travel_data)
        
        # Generate itinerary text using your LLM integration.
        itinerary_text = generate_response(travel_data)
        logging.debug("Generated itinerary text: %s", itinerary_text)
        
        # Extract keywords from the itinerary.
        extracted_keywords = extract_keywords(itinerary_text)
        logging.debug("Extracted keywords (raw): %s", extracted_keywords)
        
        # Filter out the destination to avoid repeating images for the city itself.
        destination_lower = travel_data.get("destination", "").lower()
        filtered_keywords = [kw for kw in extracted_keywords if kw.lower() != destination_lower]
        logging.debug("Filtered keywords (excluding destination): %s", filtered_keywords)
        
        augmented_items = []
        for keyword in filtered_keywords:
            # Retrieve one image URL per keyword via the DuckDuckGo scraper.
            image_url = scrape_duckduckgo_image(keyword)
            # Create a hyperlink (for example, a Google search link).
            more_info_link = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            augmented_items.append({
                "keyword": keyword,
                "image_url": image_url,
                "more_info_link": more_info_link
            })
        logging.debug("Raw augmented items: %s", augmented_items)
        
        # Deduplicate augmented items by keyword (case-insensitive).
        unique_augmented = {}
        for item in augmented_items:
            key = item["keyword"].lower()
            if key not in unique_augmented:
                unique_augmented[key] = item
        augmented_items = list(unique_augmented.values())
        logging.debug("Deduplicated augmented items: %s", augmented_items)
        
        # Dynamically format the itinerary text to include images and links.
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

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

