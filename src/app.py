import streamlit as st
import json
from planner_core import generate_plan  # backend planner function
from utils.pdf_generator import generate_pdf
from urllib.parse import quote_plus
import streamlit.components.v1 as components

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

# -----------------------------
# MAIN GENERATION LOGIC
# -----------------------------
if generate:
    if not source:
        st.error("Please enter a starting city.")
        st.stop()
    if not destinations:
        st.error("Please enter at least one destination.")
        st.stop()

    with st.spinner("🧠 Generating your custom agentic itinerary..."):
        try:
            itinerary_json = generate_plan(
                {
                    "source": source,
                    "destinations": destinations,
                    "duration": duration,
                    "budget": budget,
                    "travelers": travelers
                }
            )

            # If orchestrator returned an agentic error
            if isinstance(itinerary_json, dict) and itinerary_json.get("error"):
                st.error(
                    "⚠️ Your inputs resulted in an impossible or invalid itinerary.\n\n"
                    "Please adjust your budget, duration, or destination(s) and try again."
                )
                st.stop()

            # Parse json string if needed
            if isinstance(itinerary_json, str):
                itinerary = json.loads(itinerary_json)
            else:
                itinerary = itinerary_json

            # SAVE IN SESSION STATE
            st.session_state["itinerary"] = itinerary

        except Exception as e:
            st.error(f"⚠️ Error generating itinerary: {str(e)}")
            st.stop()

# Load itinerary from session
itinerary = st.session_state.get("itinerary", None)

if not itinerary:
    st.info("Fill in the details in the sidebar and click *Generate Itinerary* to start.")
    st.stop()

# -----------------------------
# TRIP OVERVIEW
# -----------------------------
st.markdown("## 🏖️ Trip Overview")

dest_display = itinerary.get("destination") or ", ".join(destinations) or "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("📍 From", source or "N/A")
col2.metric("📍 Destination(s)", dest_display)
col3.metric("🕒 Duration", f"{itinerary.get('duration', duration)} Days")
col4.metric("💰 Total Budget", format_inr(itinerary.get("total_budget", budget)))

st.markdown(f"**👥 Travelers:** {itinerary.get('travelers', travelers)}")

st.markdown("---")

# -----------------------------
# ACCOMMODATION PER CITY
# -----------------------------
if "city_accommodations" in itinerary:

    st.markdown("## 🏠 Accommodation (Per City)")

    hotels = itinerary["city_accommodations"]

    for entry in hotels:
        city = entry.get("city", "Unknown City")
        hotel = entry.get("hotel", "Hotel")
        htype = entry.get("type", "Stay Type")
        cost = entry.get("estimated_cost", 0)

        with st.expander(f"🏙️ {city} — {hotel}", expanded=False):

            # Basic hotel info
            st.write(f"**Type:** {htype}")
            st.write(f"**Estimated Cost:** {format_inr(cost)}")

            query = quote_plus(f"{hotel} {city}")

            google_travel = f"https://www.google.com/travel/search?q={query}"
            google_maps_search = f"https://www.google.com/maps/search/{query}"

            # Buttons row
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🏨 Book Stay", google_travel)
            with col2:
                st.link_button("📍 Open in Maps", google_maps_search)

            # Interactive map embed
            embed_url = f"https://www.google.com/maps?q={query}&output=embed"

            st.markdown("### 🗺️ Interactive Map")
            components.html(
                f"""
                <iframe 
                    width="100%" 
                    height="450" 
                    style="border:0;"
                    loading="lazy"
                    allowfullscreen 
                    referrerpolicy="no-referrer-when-downgrade"
                    src="{embed_url}">
                </iframe>
                """,
                height=450,
            )

st.markdown("---")

# -----------------------------
# TRANSPORT SECTION
# -----------------------------
if "transport" in itinerary:
    st.markdown("### 🚗 Transport")
    tr = itinerary["transport"]

    st.info( f"**Recommended:** {tr.get('recommended_transport', 'N/A')}\n\n" 
            f"**Estimated Cost:** {format_inr(tr.get('estimated_cost', 0))}" )


    # ROME2RIO LINK
    if len(destinations) > 0:
        first_dest = destinations[0]
        r2r_url = (
            f"https://www.rome2rio.com/map/"
            f"{source.replace(' ', '-')}/"
            f"{first_dest.replace(' ', '-')}"
        )
    else:
        r2r_url = "https://www.rome2rio.com"

    # GOOGLE ROUTE MAP
    route_text = itinerary.get("destination", "")
    raw_route = route_text.replace("→", ",").split(",")
    route_cities = [city.strip() for city in raw_route if city.strip()]

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚗 Book Transport", r2r_url)

    with col2:
        if len(route_cities) >= 2:
            encoded_route = "/".join([quote_plus(c) for c in route_cities])
            route_url = f"https://www.google.com/maps/dir/{encoded_route}"
            st.link_button("🧭 Full Route Map", route_url)

st.markdown("---")

# -----------------------------
# DAY-BY-DAY ITINERARY
# -----------------------------
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
        for act in activities:
            st.markdown(f"- {act}")

        st.markdown(f"**💵 Estimated Cost:** {format_inr(day_data.get('estimated_cost', 0))}")

st.markdown("---")

# -----------------------------
# DOWNLOAD PDF BUTTON  
# -----------------------------
st.markdown("## 📄 Download Your Itinerary")

if st.button("⬇️ Generate PDF"):
    try:
        pdf_file = generate_pdf(itinerary)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📄 Click to Download PDF",
                data=f,
                file_name="ATLAS_Itinerary.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

st.markdown("---")

# -----------------------------
# TOP PLACES + SUMMARY
# -----------------------------
if "top_places" in itinerary:
    st.markdown("### 🌟 Top Places to Visit")
    st.write(", ".join(itinerary["top_places"]))

if "summary" in itinerary:
    st.success(f"**Trip Summary:** {itinerary['summary']}")
