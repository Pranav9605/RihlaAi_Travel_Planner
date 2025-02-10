import streamlit as st
import requests

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
    additional_comments = st.text_area("Additional Comments", 
                                       placeholder="Enter any extra notes or preferences here...")
    submitted = st.form_submit_button("Submit")

if submitted:
    query_data = {
        "destination": destination,
        "travel_date": str(travel_date),
        "num_days": num_days,
        "budget": budget,
        "num_people": num_people,
        "travel_group": travel_group,
        "activities": activities,
        "additional_comments": additional_comments  # Include additional comments in the payload.
    }
    
    # st.write("Payload to be sent to backend:", query_data)

    with st.spinner("Fetching travel recommendations..."):
        try:
            response = requests.post("http://localhost:8000/search/", json=query_data)
            if response.status_code == 200:
                data = response.json()
                
                # st.subheader("Itinerary:")
                # st.write(data.get("itinerary", "No itinerary returned."))
                
                # st.subheader("Augmented Data (Keywords with Images & Links):")
                # st.json(data.get("augmented", {}))
                
                st.subheader("Itinerary:")
                st.markdown(data.get("rendered_output", ""), unsafe_allow_html=True)
            else:
                st.error(f"Error: Received status code {response.status_code}\n{response.text}")
        except Exception as e:
            st.error(f"Error occurred: {e}")
