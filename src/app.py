import streamlit as st
import json
from planner_core import generate_plan  # ✅ your backend planner function

st.set_page_config(page_title="Agentic Travel Planner", page_icon="✈️", layout="wide")

st.title("🌍 [ATLAS] 🌍")
st.write("Your AI-powered itinerary builder — just enter your travel details and let the planner handle the rest!")

# --- Helper Function ---
def format_inr(value):
    try:
        return f"₹{int(float(value)):,}"
    except:
        return str(value)

# --- Sidebar Input ---
with st.sidebar:
    st.header("✏️ Trip Details")
    destination = st.text_input("Destination", placeholder="e.g. Goa")
    duration = st.number_input("Trip Duration (in days)", min_value=1, step=1)
    budget = st.number_input("Total Budget (INR)", min_value=1000, step=500)
    travelers = st.number_input("Number of Travelers", min_value=1, step=1)
    generate = st.button("Generate Itinerary")

# --- Main Logic ---
if generate:
    with st.spinner("🧠 Generating your custom itinerary..."):
        try:
            # ✅ Fix argument order (destination, budget, travelers, duration)
            itinerary_json = generate_plan(destination, budget, travelers, duration)

            # Parse JSON if it's returned as a string
            if isinstance(itinerary_json, str):
                itinerary = json.loads(itinerary_json)
            else:
                itinerary = itinerary_json

            # --- UI DISPLAY STARTS HERE ---
            st.markdown("## 🏖️ Trip Overview")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📍 Destination", itinerary.get("destination", "N/A"))
            col2.metric("🕒 Duration", f"{itinerary.get('duration', '?')} Days")
            col3.metric("💰 Total Budget", format_inr(itinerary.get("total_budget", 0)))
            col4.metric("🧳 Travelers", itinerary.get("travelers", "?"))

            st.markdown("---")

            # 🏠 Accommodation Section
            if "accommodation" in itinerary:
                st.markdown("### 🏠 Accommodation")
                acc = itinerary["accommodation"]
                st.info(
                    f"**Type:** {acc.get('type', 'N/A')}\n\n"
                    f"**Example:** {acc.get('example', 'N/A')}\n\n"
                    f"**Estimated Cost:** {format_inr(acc.get('estimated_cost', 0))}"
                )

            # 🚗 Transport Section
            if "transport" in itinerary:
                st.markdown("### 🚗 Transport")
                tr = itinerary["transport"]
                st.info(
                    f"**Recommended:** {tr.get('recommended_transport', 'N/A')}\n\n"
                    f"**Estimated Cost:** {format_inr(tr.get('estimated_cost', 0))}"
                )

            st.markdown("---")

            # 📅 Per-day breakdown
            st.markdown("## 📅 Day-by-Day Itinerary")
            per_day = itinerary.get("per_day_breakdown", [])
            if isinstance(per_day, dict):
                per_day = per_day.values()

            for day_data in per_day:
                day_num = day_data.get("day", "?")
                day_title = day_data.get("title", "")
                with st.expander(f"🗓️ Day {day_num}: {day_title}"):
                    activities = day_data.get("activities", [])
                    if activities:
                        for act in activities:
                            st.markdown(f"- {act}")
                    st.markdown(f"**💵 Estimated Cost:** {format_inr(day_data.get('estimated_cost', 0))}")

            st.markdown("---")

            # 🌟 Top Places Section
            if "top_places" in itinerary:
                st.markdown("### 🌟 Top Places to Visit")
                st.write(", ".join(itinerary["top_places"]))

            # ✅ Summary
            if "summary" in itinerary:
                st.success(f"**Trip Summary:** {itinerary['summary']}")

        except Exception as e:
            st.error(f"⚠️ Error generating itinerary: {str(e)}")

else:
    st.info("Fill in the details in the sidebar and click *Generate Itinerary* to start.")
