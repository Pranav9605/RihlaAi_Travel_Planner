import openai
from backend.retrieval import retrieve_relevant_docs
from backend.config import OPENAI_API_KEY  # Ensure your config provides the OpenAI API key
import logging
import traceback

# Configure basic logging.
logging.basicConfig(level=logging.DEBUG)

# Set the OpenAI API key.
openai.api_key = OPENAI_API_KEY

def generate_response(travel_data: dict) -> str:
    """
    Generates a response to the user's travel query using OpenAI's ChatCompletion API.
    
    Args:
        travel_data (dict): A dictionary containing travel details.
        
    Returns:
        str: Generated response from OpenAI.
    """
    try:
        # Extract details with defaults if necessary.
        destination = travel_data.get("destination", "an unknown destination")
        travel_date = travel_data.get("travel_date", "an unknown date")
        num_days = travel_data.get("num_days", "a certain number of")
        budget = travel_data.get("budget", "an unspecified budget")
        num_people = travel_data.get("num_people", "an unspecified number of people")
        travel_group = travel_data.get("travel_group", "an unspecified group")
        activities = travel_data.get("activities", [])
        activities_str = ", ".join(activities) if activities else "unspecified activities"
        additional_comments = travel_data.get("additional_comments", "")
        
        # Construct the base prompt.
        prompt = (
            f"You are a helpful and informative travel assistant. Please provide a detailed answer "
            f"to the following query, including specific recommendations. Crucially, the first part of your answer "
            f"*must* suggest a specific location for the initial stay, with an explanation of why that location is chosen.\n\n"
            f"Destination: {destination}\n"
            f"Travel Date: {travel_date}\n"
            f"Duration (days): {num_days}\n"
            f"Budget: {budget}\n"
            f"Number of People: {num_people}\n"
            f"Travel Group: {travel_group}\n"
            f"Activities: {activities_str}\n"
            f"Additional Comments: {additional_comments}\n"
        )
        
        # Retrieve additional context (if any).
        docs = retrieve_relevant_docs(prompt)
        context = "\n".join(str(doc) for doc in docs)
        full_prompt = f"{prompt}\n\nAdditional Context:\n{context}"
        
        # Log the complete prompt for debugging.
        logging.debug("Full prompt for OpenAI API:\n%s", full_prompt)
        
        # Generate the response using OpenAI's ChatCompletion API.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use your desired chat model.
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=0.8,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Extract and return the assistant's reply.
        return response.choices[0].message.content.strip()
        
    except Exception:
        # Log the full traceback for troubleshooting.
        logging.error("Error generating response: %s", traceback.format_exc())
        return "I apologize, but I encountered an error while processing your request. Please try again."
