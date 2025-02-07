import google.generativeai as genai
from backend.retrieval import retrieve_relevant_docs
from backend.config import GEMINI_API_KEY
import logging
import traceback

# Configure the Gemini client with API key
genai.configure(api_key=GEMINI_API_KEY)

def setup_gemini_model():
    """Initialize and return the Gemini model."""
    model = genai.GenerativeModel('gemini-pro')
    return model

def generate_response(travel_data: dict) -> str:
    """
    Generates a response to the user's travel query using the Gemini API.
    
    Args:
        travel_data (dict): A dictionary containing travel details.
        
    Returns:
        str: Generated response from Gemini.
    """
    try:
        # Extract details with defaults if necessary
        destination = travel_data.get("destination", "an unknown destination")
        travel_date = travel_data.get("travel_date", "an unknown date")
        num_days = travel_data.get("num_days", "a certain number of")
        budget = travel_data.get("budget", "an unspecified budget")
        num_people = travel_data.get("num_people", "an unspecified number of people")
        travel_group = travel_data.get("travel_group", "an unspecified group")
        activities = travel_data.get("activities", [])
        activities_str = ", ".join(activities) if activities else "unspecified activities"
        
        # Construct a detailed prompt for the Gemini API
        prompt = (
            f"You are a helpful and informative travel assistant. Please provide a detailed answer to the following question, drawing upon the information provided. Your response should be detailed and include specific recommendations.  Crucially, the first part of your answer *must* suggest a specific location for the initial stay, explaining your reasoning for this choice.\n\n"
            f"Destination: {destination}\n"
            f"Travel Date: {travel_date}\n"
            f"Duration (days): {num_days}\n"
            f"Budget: {budget}\n"
            f"Number of People: {num_people}\n"
            f"Travel Group: {travel_group}\n"
            f"Activities: {activities_str}\n"
        )
        
        # Retrieve additional context if needed
        docs = retrieve_relevant_docs(prompt)
        context = "\n".join(str(doc) for doc in docs)
        
        full_prompt = prompt + "\n\nAdditional Context:\n" + context
        
        # Debug: log the full prompt for reference
        logging.debug("Full prompt for Gemini API:\n%s", full_prompt)
        
        # Initialize the Gemini model and generate the response
        model = setup_gemini_model()
        response = model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1024,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        )
        
        # Return the generated text
        return response.text
        
    except Exception as e:
        # Log the full traceback to diagnose the issue
        logging.error("Error generating response: %s", traceback.format_exc())
        return "I apologize, but I encountered an error while processing your request. Please try again."
