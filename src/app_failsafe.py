import streamlit as st
from planner_core import generate_plan

st.title("🌍 ATLAS - AI Travel Planner")
destination = st.text_input("Destination")
budget = st.number_input("Budget (USD)")
travelers = st.number_input("Number of Travelers", min_value=1, step=1)
duration = st.number_input("Trip Duration (days)", min_value=1, step=1)

if st.button("Plan My Trip"):
    with st.spinner("Generating your trip plan..."):
        plan = generate_plan(destination, budget, travelers, duration)
    st.success("✅ Here's your itinerary:")
    st.json(plan)
