from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile

def generate_pdf(itinerary):
    # --- PDF File in Temp Directory ---
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = temp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#1a73e8"),
        alignment=1,
        spaceAfter=20,
    )

    story = []

    # ----- TITLE -----
    story.append(Paragraph("ATLAS — Travel Itinerary", title_style))
    story.append(Spacer(1, 12))

    # ---- BASIC TRIP DETAILS ----
    def add_line(label, value):
        story.append(Paragraph(f"<b>{label}:</b> {value}", normal))
        story.append(Spacer(1, 6))

    add_line("Destination Path", itinerary.get("destination", ""))
    add_line("Duration", f"{itinerary.get('duration', '?')} days")
    add_line("Total Budget", f"₹{itinerary.get('total_budget', 0):,}")
    add_line("Travelers", itinerary.get("travelers", "?"))

    story.append(Spacer(1, 12))

    # ---- ACCOMMODATION PER CITY ----
    if "city_accommodations" in itinerary:
        story.append(Paragraph("<b>Accommodation (Per City)</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))

        for entry in itinerary["city_accommodations"]:
            city = entry.get("city", "")
            hotel = entry.get("hotel", "")
            typ = entry.get("type", "")
            cost = entry.get("estimated_cost", 0)

            story.append(Paragraph(f"<b>{city}</b>: {hotel} ({typ}) — ₹{cost:,}", normal))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 12))

    # ---- TRANSPORT ----
    if "transport" in itinerary:
        tr = itinerary["transport"]
        story.append(Paragraph("<b>Transport</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Recommended: {tr.get('recommended_transport', '')}", normal))
        story.append(Paragraph(f"Estimated Cost: ₹{tr.get('estimated_cost', 0):,}", normal))
        story.append(Spacer(1, 12))

    # ---- DAY BY DAY ----
    story.append(Paragraph("<b>Day-by-Day Itinerary</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for day in itinerary.get("per_day_breakdown", []):
        day_title = f"Day {day.get('day')} — {day.get('title')}"
        story.append(Paragraph(f"<b>{day_title}</b>", normal))
        story.append(Spacer(1, 6))

        for act in day.get("activities", []):
            story.append(Paragraph(f"- {act}", normal))
        story.append(Paragraph(f"<b>Estimated Cost:</b> ₹{day.get('estimated_cost', 0):,}", normal))
        story.append(Spacer(1, 12))

    # ---- SUMMARY ----
    if "summary" in itinerary:
        story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(itinerary["summary"], normal))

    # ---- BUILD PDF ----
    doc.build(story)
    return pdf_path
