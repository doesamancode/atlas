import streamlit as st
import json
from planner_core import generate_plan
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

# Sidebar Input
with st.sidebar:
    st.header("✏️ Trip Details")

    source = st.text_input("Starting City", placeholder="e.g. Delhi")

    destinations_raw = st.text_input(
        "Destination(s)",
        placeholder="e.g. Goa, Kochi, Munnar"
    )
    destinations = [d.strip() for d in destinations_raw.split(",") if d.strip()]

    duration = st.number_input("Trip Duration (days)", min_value=1, step=1)
    budget = st.number_input("Total Budget (INR)", min_value=2000, step=1000)
    travelers = st.number_input("Number of Travelers", min_value=1, step=1)

    generate = st.button("Generate Itinerary")

# -------------------------------
# MAIN LOGIC (spinner only here)
# -------------------------------
if generate:
    if not source:
        st.error("Please enter a starting city.")
        st.stop()
    if not destinations:
        st.error("Please enter at least one destination.")
        st.stop()
    if "aligrh" in destinations:
        st.markdown("## **I don't know bruh ask DJ** 🥀💔😢 \ndont kirk me")
        st.stop()

    with st.spinner("🧠 Building your trip with our agents..."):
        try:
            result = generate_plan({
                "source": source,
                "destinations": destinations,
                "duration": duration,
                "budget": budget,
                "travelers": travelers
            })
            st.session_state["result"] = result

        except Exception as e:
            st.session_state["result"] = {"error": "pipeline_crash", "reasons": [str(e)]}

# -------------------------------
# POST-SPINNER: UI + Validation
# -------------------------------
result = st.session_state.get("result")

if not result:
    st.info("Fill in travel details and click *Generate Itinerary* to start.")
    st.stop()

if result.get("error"):
    reasons = result.get("reasons", ["Unknown itinerary failure"])
    if isinstance(reasons, list):
        msg = "\n".join(f"- {r}" for r in reasons)
    else:
        msg = reasons
    st.error(f"⚠️ Itinerary could not be generated:\n\n{msg}")
    st.stop()

# If success, rename to itinerary
itinerary = result
st.session_state["itinerary"] = itinerary

# -------------------------------
# ITINERARY DISPLAY
# -------------------------------
st.markdown("## 🏖️ Trip Overview")

dest_display = itinerary.get("destination") or ", ".join(destinations)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📍 From", source)
col2.metric("📍 Destinations", dest_display)
col3.metric("🕒 Duration", f"{itinerary.get('duration', duration)} Days")
col4.metric("💰 Total Budget", format_inr(itinerary.get("total_budget", budget)))

st.markdown(f"**👥 Travelers:** {itinerary.get('travelers', travelers)}")
st.markdown("---")

# -------------------------------
# ACCOMMODATIONS
# -------------------------------
if "city_accommodations" in itinerary:

    st.markdown("## 🏠 Accommodation (Per City)")
    hotels = itinerary["city_accommodations"]

    for entry in hotels:
        city = entry.get("city", "Unknown City")
        hotel = entry.get("hotel", "Hotel")
        htype = entry.get("type", "Stay Type")
        cost = entry.get("estimated_cost", 0)

        with st.expander(f"🏙️ {city} — {hotel}"):
            st.write(f"**Type:** {htype}")
            st.write(f"**Estimated Cost:** {format_inr(cost)}")

            query = quote_plus(f"{hotel} {city}")
            st.link_button("🏨 Book Stay", f"https://www.google.com/travel/search?q={query}")
            st.link_button("📍 Open in Maps", f"https://www.google.com/maps/search/{query}")

            st.markdown("### 🗺️ Interactive Map")
            components.html(
                f"""
                <iframe width="100%" height="450" style="border:0;"
                src="https://www.google.com/maps?q={query}&output=embed"
                loading="lazy" allowfullscreen></iframe>
                """,
                height=450,
            )

st.markdown("---")

# -------------------------------
# TRANSPORT
# -------------------------------
if "transport" in itinerary:
    st.markdown("### 🚗 Transport")
    tr = itinerary["transport"]

    st.info(
        f"**Recommended:** {tr.get('recommended_transport')}\n\n"
        f"**Estimated Cost:** {format_inr(tr.get('estimated_cost'))}"
    )

    # Transport Buttons
    colA, colB = st.columns(2)
    with colA:
        st.link_button("🚗 Book Transport",
                       f"https://www.rome2rio.com/map/{source.replace(' ', '-')}/{destinations[0].replace(' ', '-')}")
    with colB:
        encoded_route = "/".join(quote_plus(c) for c in itinerary.get("destination", "").split("→"))
        st.link_button("🧭 Full Route Map", f"https://www.google.com/maps/dir/{encoded_route}")

st.markdown("---")

# -------------------------------
# PER-DAY PLAN
# -------------------------------
st.markdown("## 📅 Day-by-Day Plan")

for day in itinerary.get("per_day_breakdown", []):
    label = f"🗓️ Day {day.get('day')}: {day.get('title')}"
    if day.get("city"):
        label += f" — 🏙️ {day['city']}"

    with st.expander(label):
        for act in day.get("activities", []):
            st.markdown(f"- {act}")
        st.markdown(f"**💵 Estimated Cost:** {format_inr(day.get('estimated_cost'))}")

st.markdown("---")

# -------------------------------
# PDF DOWNLOAD
# -------------------------------
st.markdown("## 📄 Download Your Itinerary")
if st.button("⬇️ Generate PDF"):
    pdf_file = generate_pdf(itinerary)
    with open(pdf_file, "rb") as f:
        st.download_button("📄 Click to Download PDF", f, "ATLAS_Itinerary.pdf", "application/pdf")

st.markdown("---")

# -------------------------------
# FINAL INFO SECTIONS
# -------------------------------
if "top_places" in itinerary:
    st.markdown("### 🌟 Top Places to Visit")
    st.write(", ".join(itinerary["top_places"]))

if "summary" in itinerary:
    st.success(f"**Trip Summary:** {itinerary['summary']}")
