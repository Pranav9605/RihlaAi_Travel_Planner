import streamlit as st
import requests
from datetime import datetime
import concurrent.futures

st.title("RihlaAi: Your AI-Powered Passport to Arabia")

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
    additional_comments = st.text_area(
        "Additional Comments", 
        placeholder="Enter any extra notes or preferences here..."
    )
    submitted = st.form_submit_button("Submit")

if submitted:
    # Build payload for travel recommendations.
    query_data = {
        "destination": destination,
        "travel_date": str(travel_date),
        "num_days": num_days,
        "budget": budget,
        "num_people": num_people,
        "travel_group": travel_group,
        "activities": activities,
        "additional_comments": additional_comments
    }
    # st.write("Payload to be sent to backend:", query_data)
    
    # Prepare forecast payload.
    # Convert travel_date to a datetime string with default time "00:00:00".
    travel_date_str = travel_date.strftime("%Y-%m-%d 00:00:00")
    forecast_payload = {
        "target_date": travel_date_str,
        "threshold": 25.0  # Predefined temperature threshold.
    }
    
    with st.spinner("Fetching travel recommendations and weather forecast..."):
        # Use ThreadPoolExecutor to run both requests concurrently.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_travel = executor.submit(requests.post, "http://localhost:8000/search/", json=query_data)
            future_forecast = executor.submit(requests.post, "http://localhost:8000/forecast/", json=forecast_payload)
            
            travel_response = future_travel.result()
            forecast_response = future_forecast.result()
        
        # Process travel recommendations response.
        if travel_response.status_code == 200:
            travel_data = travel_response.json()
            st.subheader("Itinerary:")
            st.markdown(travel_data.get("rendered_output", "No itinerary returned."), unsafe_allow_html=True)
        else:
            st.error(f"Travel Recommendations Error: Received status code {travel_response.status_code}\n{travel_response.text}")
        
        # Process weather forecast response.
        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            st.subheader("Weather Forecast:")
            st.write(forecast_data.get("forecast", "No forecast returned."))
        else:
            st.error(f"Weather Forecast Error: Received status code {forecast_response.status_code}\n{forecast_response.text}")
