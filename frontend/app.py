import streamlit as st
import requests

import streamlit as st



st.title("RihlaAi: Your AI-Powered Passport to Arabia")

# Define the form for travel preferences
with st.form("travel_preferences_form"):
    destination = st.text_input("Destination")
    travel_date = st.date_input("Travel Date (start)")
    num_days = st.number_input("Number of days for travel", min_value=1, step=1)
    budget = st.selectbox("Budget", ["Low", "Medium", "High"])
    num_people = st.number_input("Number of people traveling", min_value=1, step=1)
    travel_group = st.radio("Group Type", ["Family", "Couple", "Friends"])
    activities = st.multiselect(
        "Interested Activities", 
        ["Beaches", "City Exploration", "Nightlife", "Food Tours", "Events"]
    )
    # Submit button inside the form
    submitted = st.form_submit_button("Submit")

# This block runs only after the user submits the form
if submitted:
    # Construct the query payload as a dictionary
    query_data = {
        "destination": destination,
        "travel_date": str(travel_date),  # Convert date to string for JSON serialization
        "num_days": num_days,
        "budget": budget,
        "num_people": num_people,
        "travel_group": travel_group,
        "activities": activities
    }
    
    # Optionally, display the payload for debugging
    st.write("Payload to be sent to backend:", query_data)

    # Make a POST request to the FastAPI backend
    with st.spinner("Fetching travel recommendations..."):
        try:
            response = requests.post("http://localhost:8000/search/", json=query_data)
            # Check if the response status is OK
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    st.success("Travel Recommendations:")
                    st.write(data["response"])
                else:
                    st.error("Error: 'response' key not found in the response data.")
            else:
                st.error(f"Error: Received status code {response.status_code}\n{response.text}")
        except Exception as e:
            st.error(f"Error occurred: {e}")
