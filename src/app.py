import streamlit as st
import json
from planner_core import generate_plan  # backend planner function

st.set_page_config(page_title="ATLAS - Agentic Travel Planner", page_icon="✈️", layout="wide")

st.title("🌍 [ATLAS] Multi-Destination Planner 🌍")
st.write("Your AI-powered, agentic travel planner — now with multi-city itineraries.")

def format_inr(value):
    try:
        return f"₹{int(float(value)):,}"
    except:
        return str(value)

# Sidebar input
with st.sidebar:
    st.header("✏️ Trip Details")

    source = st.text_input("Starting City", placeholder="e.g. Delhi")

    destinations_raw = st.text_input(
        "Destination(s)",
        placeholder="e.g. Goa, Kochi, Munnar"
    )
    destinations = [d.strip() for d in destinations_raw.split(",") if d.strip()]

    duration = st.number_input("Trip Duration (in days)", min_value=1, step=1)
    budget = st.number_input("Total Budget (INR)", min_value=1000, step=500)
    travelers = st.number_input("Number of Travelers", min_value=1, step=1)

    generate = st.button("Generate Itinerary")

# Main app logic
if generate:
    # basic input validation
    if not source:
        st.error("Please enter a starting city.")
    elif not destinations:
        st.error("Please enter at least one destination (comma-separated).")
    else:
        with st.spinner("🧠 Generating your custom agentic itinerary..."):
            try:
                # Call agentic planner: source + list of destinations
                itinerary_json = generate_plan(source, destinations, budget, travelers, duration)

                # 🔴 Agentic error handling (from orchestrator)
                if isinstance(itinerary_json, dict) and itinerary_json.get("error"):
                    st.error(
                        "⚠️ Your inputs resulted in an impossible or invalid itinerary.\n\n"
                        "Please adjust your budget, duration, or destination(s) and try again."
                    )
                    st.stop()

                # Parse JSON if returned as a string
                if isinstance(itinerary_json, str):
                    itinerary = json.loads(itinerary_json)
                else:
                    itinerary = itinerary_json

                # --- UI DISPLAY STARTS HERE ---
                st.markdown("## 🏖️ Trip Overview")

                dest_display = itinerary.get("destination") or ", ".join(destinations) or "N/A"

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📍 From", source or "N/A")
                col2.metric("📍 Destination(s)", dest_display)
                col3.metric("🕒 Duration", f"{itinerary.get('duration', duration)} Days")
                col4.metric("💰 Total Budget", format_inr(itinerary.get("total_budget", budget)))

                st.markdown(f"**👥 Travelers:** {itinerary.get('travelers', travelers)}")

                st.markdown("---")

                # 🏠 ULTRA PRO: Per-City Accommodation Section
                if "city_accommodations" in itinerary:
                
                    st.markdown("## 🏠 Accommodation (Per City)")
                
                    from urllib.parse import quote_plus
                
                    hotels = itinerary["city_accommodations"]
                
                    for entry in hotels:
                        city = entry.get("city", "Unknown City")
                        hotel = entry.get("hotel", "Hotel")
                        htype = entry.get("type", "Stay Type")
                        cost = entry.get("estimated_cost", 0)
                
                        with st.expander(f"🏙️ {city} — {hotel}"):
                            st.write(f"**Type:** {htype}")
                            st.write(f"**Estimated Cost:** {format_inr(cost)}")
                
                            # Links
                            query = quote_plus(f"{hotel} {city}")
                            google_travel = f"https://www.google.com/travel/search?q={query}"
                            google_maps = f"https://www.google.com/maps/search/{query}"
                
                            col1, col2 = st.columns(2)
                            with col1:
                                st.link_button("🏨 Book Stay", google_travel)
                            with col2:
                                st.link_button("📍 View on Maps", google_maps)
                
                    st.markdown("---")
                
                # Fallback (old field)
                elif "accommodation" in itinerary:
                    st.markdown("## 🏠 Accommodation")
                    st.warning("Per-city hotel data missing. Try regenerating with a different model.")

                
                # 🚗 Transport Section
                if "transport" in itinerary:
                    st.markdown("### 🚗 Transport")
                    tr = itinerary["transport"]
                    st.info(
                        f"**Recommended:** {tr.get('recommended_transport', 'N/A')}\n\n"
                        f"**Estimated Cost:** {format_inr(tr.get('estimated_cost', 0))}"
                    )
                
                    # ⭐ TRANSPORT BOOKING BUTTON (ROME2RIO)
                    source_city = source.strip() if isinstance(source, str) else ""
                
                    if isinstance(destinations, list) and len(destinations) > 0:
                        first_dest = destinations[0]
                    else:
                        first_dest = itinerary.get("destination", "")
                
                    if source_city and first_dest:
                        route_url = (
                            f"https://www.rome2rio.com/map/"
                            f"{source_city.replace(' ', '-')}/"
                            f"{first_dest.replace(' ', '-')}"
                        )
                        st.link_button("🚗 Book Transport", route_url)
                
                st.markdown("---")


                # 📅 Per-day breakdown
                st.markdown("## 📅 Day-by-Day Itinerary")
                per_day = itinerary.get("per_day_breakdown", [])
                if isinstance(per_day, dict):
                    per_day = per_day.values()

                for day_data in per_day:
                    day_num = day_data.get("day", "?")
                    day_title = day_data.get("title", "")
                    city_tag = day_data.get("city", "")
                    header = f"🗓️ Day {day_num}: {day_title}"
                    if city_tag:
                        header += f" — 🏙️ {city_tag}"

                    with st.expander(header):
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
