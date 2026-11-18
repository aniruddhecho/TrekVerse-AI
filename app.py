import math
import io
import json
import random
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# ============================================================
# TREKVERSE V6 — India Travel Planner
# A single-file Streamlit app. Estimates are illustrative only.
# ============================================================

st.set_page_config(
    page_title="TrekVerse | India Travel Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

DESTINATIONS = [
    {"place":"Indore","state":"Madhya Pradesh","region":"Central India","type":"Food & Culture","months":"October–March","daily":1800,"stay":1100,"lat":22.7196,"lon":75.8577,"tags":["food","culture","city","heritage"],"about":"A lively city known for street food, markets and nearby heritage sites."},
    {"place":"Ujjain","state":"Madhya Pradesh","region":"Central India","type":"Spiritual","months":"October–March","daily":1600,"stay":900,"lat":23.1765,"lon":75.7885,"tags":["spiritual","culture","heritage"],"about":"An important pilgrimage city on the Shipra River."},
    {"place":"Bhopal","state":"Madhya Pradesh","region":"Central India","type":"Nature & Culture","months":"October–March","daily":1900,"stay":1100,"lat":23.2599,"lon":77.4126,"tags":["nature","culture","lake","city"],"about":"A city of lakes, museums and nearby wildlife destinations."},
    {"place":"Pachmarhi","state":"Madhya Pradesh","region":"Central India","type":"Nature","months":"October–June","daily":2300,"stay":1400,"lat":22.4674,"lon":78.4331,"tags":["nature","hills","waterfalls","adventure"],"about":"A hill station with forest trails, viewpoints and waterfalls."},
    {"place":"Khajuraho","state":"Madhya Pradesh","region":"Central India","type":"Heritage","months":"October–March","daily":2200,"stay":1300,"lat":24.8318,"lon":79.9199,"tags":["heritage","culture","architecture"],"about":"Famous for its historic temple architecture."},
    {"place":"Orchha","state":"Madhya Pradesh","region":"Central India","type":"Heritage","months":"October–March","daily":1900,"stay":1100,"lat":25.3519,"lon":78.6407,"tags":["heritage","culture","river"],"about":"A historic town with palaces, cenotaphs and riverside scenery."},
    {"place":"Jabalpur","state":"Madhya Pradesh","region":"Central India","type":"Nature","months":"October–March","daily":2100,"stay":1200,"lat":23.1815,"lon":79.9864,"tags":["nature","waterfalls","river"],"about":"Gateway to marble rocks, waterfalls and forest reserves."},
    {"place":"Amarkantak","state":"Madhya Pradesh","region":"Central India","type":"Nature & Spiritual","months":"October–March","daily":1800,"stay":1000,"lat":22.6745,"lon":81.7597,"tags":["nature","spiritual","hills"],"about":"A forested pilgrimage destination and source region of rivers."},
    {"place":"Jaipur","state":"Rajasthan","region":"North India","type":"Heritage","months":"October–March","daily":2600,"stay":1600,"lat":26.9124,"lon":75.7873,"tags":["heritage","culture","shopping","food"],"about":"The Pink City, known for forts, palaces, crafts and food."},
    {"place":"Udaipur","state":"Rajasthan","region":"North India","type":"Romantic & Heritage","months":"September–March","daily":3000,"stay":1900,"lat":24.5854,"lon":73.7125,"tags":["heritage","lake","culture","romantic"],"about":"A lakeside city with palaces, old streets and scenic views."},
    {"place":"Jodhpur","state":"Rajasthan","region":"North India","type":"Heritage","months":"October–March","daily":2400,"stay":1400,"lat":26.2389,"lon":73.0243,"tags":["heritage","culture","desert"],"about":"The Blue City, dominated by Mehrangarh Fort."},
    {"place":"Jaisalmer","state":"Rajasthan","region":"North India","type":"Desert","months":"October–February","daily":2800,"stay":1700,"lat":26.9157,"lon":70.9083,"tags":["desert","adventure","culture","heritage"],"about":"Golden sandstone architecture and Thar Desert experiences."},
    {"place":"Pushkar","state":"Rajasthan","region":"North India","type":"Spiritual & Culture","months":"October–March","daily":2200,"stay":1300,"lat":26.4899,"lon":74.6399,"tags":["spiritual","culture","lake"],"about":"A pilgrimage town known for its lake and annual fair."},
    {"place":"Mount Abu","state":"Rajasthan","region":"North India","type":"Hill Station","months":"October–March","daily":2500,"stay":1500,"lat":24.5926,"lon":72.7156,"tags":["hills","nature","lake"],"about":"Rajasthan's hill station with viewpoints and temples."},
    {"place":"Delhi","state":"Delhi","region":"North India","type":"City & Heritage","months":"October–March","daily":2800,"stay":1700,"lat":28.6139,"lon":77.2090,"tags":["city","heritage","food","shopping"],"about":"A capital city with historic monuments, markets and museums."},
    {"place":"Agra","state":"Uttar Pradesh","region":"North India","type":"Heritage","months":"October–March","daily":2300,"stay":1300,"lat":27.1767,"lon":78.0081,"tags":["heritage","architecture","culture"],"about":"Home to the Taj Mahal and other Mughal-era landmarks."},
    {"place":"Varanasi","state":"Uttar Pradesh","region":"North India","type":"Spiritual & Culture","months":"October–March","daily":2200,"stay":1200,"lat":25.3176,"lon":82.9739,"tags":["spiritual","culture","river","food"],"about":"An ancient riverside city with ghats, temples and traditions."},
    {"place":"Rishikesh","state":"Uttarakhand","region":"North India","type":"Adventure & Spiritual","months":"September–June","daily":2500,"stay":1400,"lat":30.0869,"lon":78.2676,"tags":["adventure","river","spiritual","yoga","nature"],"about":"Known for river activities, yoga and Himalayan foothill scenery."},
    {"place":"Haridwar","state":"Uttarakhand","region":"North India","type":"Spiritual","months":"October–March","daily":1900,"stay":1000,"lat":29.9457,"lon":78.1642,"tags":["spiritual","river","culture"],"about":"A major pilgrimage city on the Ganges."},
    {"place":"Mussoorie","state":"Uttarakhand","region":"North India","type":"Hill Station","months":"March–June; September–November","daily":2800,"stay":1700,"lat":30.4598,"lon":78.0644,"tags":["hills","nature","shopping"],"about":"A popular hill station with mountain views and walking streets."},
    {"place":"Nainital","state":"Uttarakhand","region":"North India","type":"Hill Station","months":"March–June; September–November","daily":2700,"stay":1600,"lat":29.3803,"lon":79.4636,"tags":["hills","lake","nature"],"about":"A lake town surrounded by forested hills."},
    {"place":"Manali","state":"Himachal Pradesh","region":"North India","type":"Adventure & Hill Station","months":"March–June; October–November","daily":3200,"stay":1900,"lat":32.2432,"lon":77.1892,"tags":["hills","adventure","snow","nature"],"about":"A mountain destination for scenic drives and outdoor activities."},
    {"place":"Shimla","state":"Himachal Pradesh","region":"North India","type":"Hill Station","months":"March–June; December–January","daily":2900,"stay":1800,"lat":31.1048,"lon":77.1734,"tags":["hills","heritage","shopping"],"about":"A historic hill station with colonial-era architecture."},
    {"place":"Dharamshala","state":"Himachal Pradesh","region":"North India","type":"Nature & Culture","months":"March–June; September–November","daily":2700,"stay":1600,"lat":32.2190,"lon":76.3234,"tags":["hills","nature","culture","spiritual"],"about":"A Himalayan town known for mountain scenery and Tibetan culture."},
    {"place":"Leh","state":"Ladakh","region":"North India","type":"Adventure","months":"June–September","daily":4200,"stay":2500,"lat":34.1526,"lon":77.5771,"tags":["adventure","mountains","culture"],"about":"High-altitude landscapes, monasteries and mountain passes. Acclimatise carefully."},
    {"place":"Srinagar","state":"Jammu and Kashmir","region":"North India","type":"Nature","months":"April–October","daily":3500,"stay":2100,"lat":34.0837,"lon":74.7973,"tags":["nature","lake","mountains","culture"],"about":"Known for Dal Lake, gardens and Himalayan scenery."},
    {"place":"Amritsar","state":"Punjab","region":"North India","type":"Culture & Food","months":"October–March","daily":2300,"stay":1300,"lat":31.6340,"lon":74.8723,"tags":["culture","food","heritage","spiritual"],"about":"A major cultural destination with the Golden Temple and Punjabi cuisine."},
    {"place":"Chandigarh","state":"Chandigarh","region":"North India","type":"City","months":"October–March","daily":2500,"stay":1500,"lat":30.7333,"lon":76.7794,"tags":["city","architecture","nature"],"about":"A planned city known for architecture and gardens."},
    {"place":"Kolkata","state":"West Bengal","region":"East India","type":"Culture & Food","months":"October–March","daily":2300,"stay":1400,"lat":22.5726,"lon":88.3639,"tags":["city","culture","food","heritage"],"about":"A cultural capital with colonial landmarks, art and food."},
    {"place":"Darjeeling","state":"West Bengal","region":"East India","type":"Hill Station","months":"March–May; October–December","daily":3000,"stay":1800,"lat":27.0360,"lon":88.2627,"tags":["hills","nature","tea","mountains"],"about":"A Himalayan hill town famous for tea gardens and mountain views."},
    {"place":"Gangtok","state":"Sikkim","region":"East India","type":"Mountain & Culture","months":"March–June; September–November","daily":3200,"stay":1900,"lat":27.3314,"lon":88.6138,"tags":["mountains","nature","culture"],"about":"A mountain capital and base for exploring Sikkim."},
    {"place":"Shillong","state":"Meghalaya","region":"East India","type":"Nature","months":"October–April","daily":2800,"stay":1600,"lat":25.5788,"lon":91.8933,"tags":["nature","hills","music","waterfalls"],"about":"A hill city surrounded by waterfalls and green landscapes."},
    {"place":"Cherrapunji","state":"Meghalaya","region":"East India","type":"Nature & Adventure","months":"October–May","daily":3000,"stay":1700,"lat":25.2702,"lon":91.7323,"tags":["nature","waterfalls","adventure","hills"],"about":"Known for dramatic cliffs, caves and waterfalls."},
    {"place":"Kaziranga","state":"Assam","region":"East India","type":"Wildlife","months":"November–April","daily":3500,"stay":2000,"lat":26.5775,"lon":93.1711,"tags":["wildlife","nature","adventure"],"about":"A major wildlife destination; safari access is seasonal and regulated."},
    {"place":"Puri","state":"Odisha","region":"East India","type":"Beach & Spiritual","months":"October–February","daily":2300,"stay":1300,"lat":19.8135,"lon":85.8312,"tags":["beach","spiritual","culture","food"],"about":"A coastal pilgrimage destination with a long beach."},
    {"place":"Bhubaneswar","state":"Odisha","region":"East India","type":"Heritage","months":"October–March","daily":2100,"stay":1200,"lat":20.2961,"lon":85.8245,"tags":["heritage","culture","temples"],"about":"Known for historic temples and nearby heritage sites."},
    {"place":"Mumbai","state":"Maharashtra","region":"West India","type":"City & Food","months":"November–February","daily":3500,"stay":2200,"lat":19.0760,"lon":72.8777,"tags":["city","food","beach","shopping"],"about":"A major coastal metropolis with food, arts and iconic landmarks."},
    {"place":"Pune","state":"Maharashtra","region":"West India","type":"City & Heritage","months":"October–February","daily":2600,"stay":1500,"lat":18.5204,"lon":73.8567,"tags":["city","food","heritage","nature"],"about":"A city with historic forts, food and nearby hill country."},
    {"place":"Mahabaleshwar","state":"Maharashtra","region":"West India","type":"Hill Station","months":"October–June","daily":2800,"stay":1700,"lat":17.9307,"lon":73.6477,"tags":["hills","nature","strawberry"],"about":"A hill station with viewpoints, forests and strawberry farms."},
    {"place":"Lonavala","state":"Maharashtra","region":"West India","type":"Hill Station","months":"June–February","daily":2400,"stay":1400,"lat":18.7546,"lon":73.4062,"tags":["hills","nature","waterfalls"],"about":"A popular short-break destination in the Western Ghats."},
    {"place":"Goa","state":"Goa","region":"West India","type":"Beach","months":"November–February","daily":3500,"stay":2200,"lat":15.2993,"lon":74.1240,"tags":["beach","food","nightlife","water sports"],"about":"A coastal destination with beaches, heritage and seafood."},
    {"place":"Ahmedabad","state":"Gujarat","region":"West India","type":"Culture & Food","months":"November–February","daily":2300,"stay":1300,"lat":23.0225,"lon":72.5714,"tags":["heritage","food","culture","city"],"about":"A UNESCO-listed historic city with architecture and food."},
    {"place":"Kutch","state":"Gujarat","region":"West India","type":"Desert & Culture","months":"November–February","daily":3000,"stay":1700,"lat":23.7337,"lon":69.8597,"tags":["desert","culture","nature","festival"],"about":"Known for the White Rann and regional crafts."},
    {"place":"Dwarka","state":"Gujarat","region":"West India","type":"Spiritual & Coastal","months":"October–March","daily":2200,"stay":1200,"lat":22.2442,"lon":68.9685,"tags":["spiritual","coast","culture"],"about":"A coastal pilgrimage town in Gujarat."},
    {"place":"Somnath","state":"Gujarat","region":"West India","type":"Spiritual & Coastal","months":"October–March","daily":2200,"stay":1200,"lat":20.8880,"lon":70.4012,"tags":["spiritual","coast","heritage"],"about":"A coastal town known for its historic temple."},
    {"place":"Hyderabad","state":"Telangana","region":"South India","type":"City & Food","months":"October–February","daily":2600,"stay":1500,"lat":17.3850,"lon":78.4867,"tags":["city","food","heritage","shopping"],"about":"A city famous for its food, forts and historic architecture."},
    {"place":"Hampi","state":"Karnataka","region":"South India","type":"Heritage","months":"October–February","daily":2300,"stay":1200,"lat":15.3350,"lon":76.4600,"tags":["heritage","history","architecture","nature"],"about":"A remarkable landscape of historic Vijayanagara ruins."},
    {"place":"Bengaluru","state":"Karnataka","region":"South India","type":"City","months":"October–February","daily":3000,"stay":1800,"lat":12.9716,"lon":77.5946,"tags":["city","food","parks","shopping"],"about":"A modern city with gardens, food and cultural spaces."},
    {"place":"Mysuru","state":"Karnataka","region":"South India","type":"Heritage","months":"October–February","daily":2400,"stay":1400,"lat":12.2958,"lon":76.6394,"tags":["heritage","culture","palace","food"],"about":"Known for its palace, markets and cultural traditions."},
    {"place":"Coorg","state":"Karnataka","region":"South India","type":"Nature","months":"October–March","daily":3000,"stay":1800,"lat":12.3375,"lon":75.8069,"tags":["nature","coffee","hills","waterfalls"],"about":"A green hill region known for coffee estates and forests."},
    {"place":"Gokarna","state":"Karnataka","region":"South India","type":"Beach","months":"October–March","daily":2600,"stay":1500,"lat":14.5479,"lon":74.3188,"tags":["beach","nature","trekking"],"about":"A coastal town with beaches and walking trails."},
    {"place":"Chennai","state":"Tamil Nadu","region":"South India","type":"City & Coast","months":"November–February","daily":2700,"stay":1600,"lat":13.0827,"lon":80.2707,"tags":["city","beach","culture","food"],"about":"A coastal metropolis with temples, arts and food."},
    {"place":"Ooty","state":"Tamil Nadu","region":"South India","type":"Hill Station","months":"October–June","daily":2800,"stay":1700,"lat":11.4102,"lon":76.6950,"tags":["hills","nature","tea"],"about":"A Nilgiri hill station with gardens and tea estates."},
    {"place":"Kodaikanal","state":"Tamil Nadu","region":"South India","type":"Hill Station","months":"October–June","daily":2700,"stay":1600,"lat":10.2381,"lon":77.4892,"tags":["hills","nature","lake"],"about":"A hill town known for its lake and forest walks."},
    {"place":"Madurai","state":"Tamil Nadu","region":"South India","type":"Heritage & Spiritual","months":"October–March","daily":2100,"stay":1200,"lat":9.9252,"lon":78.1198,"tags":["heritage","spiritual","culture","food"],"about":"An ancient city centred around the Meenakshi temple."},
    {"place":"Rameswaram","state":"Tamil Nadu","region":"South India","type":"Coastal & Spiritual","months":"October–April","daily":2300,"stay":1300,"lat":9.2876,"lon":79.3129,"tags":["coast","spiritual","nature"],"about":"A pilgrimage island with beaches and coastal landscapes."},
    {"place":"Kochi","state":"Kerala","region":"South India","type":"Coastal & Culture","months":"October–March","daily":3000,"stay":1800,"lat":9.9312,"lon":76.2673,"tags":["coast","culture","food","heritage"],"about":"A port city with historic neighbourhoods and waterfronts."},
    {"place":"Munnar","state":"Kerala","region":"South India","type":"Hill Station","months":"September–March","daily":3200,"stay":1900,"lat":10.0889,"lon":77.0595,"tags":["hills","nature","tea","wildlife"],"about":"A hill destination surrounded by tea plantations."},
    {"place":"Alappuzha","state":"Kerala","region":"South India","type":"Backwaters","months":"October–March","daily":3200,"stay":1900,"lat":9.4981,"lon":76.3388,"tags":["backwaters","nature","water"],"about":"Known for Kerala backwaters and houseboat experiences."},
    {"place":"Wayanad","state":"Kerala","region":"South India","type":"Nature & Wildlife","months":"October–May","daily":2800,"stay":1600,"lat":11.6854,"lon":76.1320,"tags":["nature","wildlife","hills","waterfalls"],"about":"A green district with forests, waterfalls and trekking areas."},
    {"place":"Kovalam","state":"Kerala","region":"South India","type":"Beach","months":"October–March","daily":3000,"stay":1800,"lat":8.4004,"lon":76.9787,"tags":["beach","coast","relaxation"],"about":"A beach destination near Thiruvananthapuram."},
    {"place":"Pondicherry","state":"Puducherry","region":"South India","type":"Coastal & Culture","months":"October–March","daily":2800,"stay":1700,"lat":11.9416,"lon":79.8083,"tags":["coast","culture","food","heritage"],"about":"A coastal town known for its promenade and French-influenced quarter."},
    {"place":"Visakhapatnam","state":"Andhra Pradesh","region":"South India","type":"Coastal","months":"October–March","daily":2400,"stay":1400,"lat":17.6868,"lon":83.2185,"tags":["coast","beach","nature"],"about":"A port city with beaches and nearby hill landscapes."},
    {"place":"Tirupati","state":"Andhra Pradesh","region":"South India","type":"Spiritual","months":"September–March","daily":2100,"stay":1100,"lat":13.6288,"lon":79.4192,"tags":["spiritual","nature","culture"],"about":"A major pilgrimage destination in the Tirumala hills."},
    {"place":"Andaman Islands","state":"Andaman and Nicobar Islands","region":"Islands","type":"Beach & Adventure","months":"October–May","daily":5000,"stay":3000,"lat":11.7401,"lon":92.6586,"tags":["beach","island","adventure","water sports"],"about":"An island destination with beaches, reefs and water activities."},
    {"place":"Lakshadweep","state":"Lakshadweep","region":"Islands","type":"Island & Nature","months":"October–March","daily":6000,"stay":3500,"lat":10.5667,"lon":72.6417,"tags":["beach","island","nature","water sports"],"about":"A coral island group with permit and travel requirements."},
]

INTERESTS = ["nature","adventure","beach","heritage","culture","food","spiritual","hills","wildlife","shopping","lake","waterfalls","island","coast","desert"]

def estimate_cost(destination, days, travellers, travel_fare_per_person=0):
    """Return a transparent illustrative group-cost estimate."""
    stay = int(destination["stay"] * days * travellers)
    food = int(destination["daily"] * 0.30 * days * travellers)
    local = int(destination["daily"] * 0.15 * days * travellers)
    activities = int(destination["daily"] * 0.20 * days * travellers)
    intercity = int(max(0, travel_fare_per_person) * travellers)
    return {
        "stay": stay,
        "food": food,
        "local": local,
        "activities": activities,
        "intercity": intercity,
        "total": stay + food + local + activities + intercity,
    }

def rank_destinations(origin, budget, days, travellers, selected_interests, max_results=12):
    results = []
    for d in DESTINATIONS:
        cost = estimate_cost(d, days, travellers)
        interest_score = sum(1 for tag in selected_interests if tag in d["tags"])
        budget_fit = 1.0 if cost["total"] <= budget else max(0.0, budget / max(cost["total"], 1))
        same_state_bonus = 0.15 if origin.strip().lower() == d["state"].lower() else 0
        score = interest_score * 2 + budget_fit * 3 + same_state_bonus
        results.append((score, cost["total"], d, cost))
    results.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    affordable = [x for x in results if x[1] <= budget]
    return (affordable or results)[:max_results]

def maps_url(place):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(place + ", India")

def make_itinerary(destination, days, interests):
    day_plans = []
    ideas = [
        ["Arrive, check in and explore the main market or town centre.", "Visit a well-known local landmark.", "Try a regional meal and take an easy evening walk."],
        ["Start with the destination's main attraction.", "Explore a nearby nature, heritage or cultural site.", "Keep the evening flexible for local food."],
        ["Choose a guided local experience or short outdoor activity.", "Visit a viewpoint, museum or neighbourhood.", "Return early and prepare for the next day."],
        ["Explore a nearby day-trip location.", "Keep time for shopping and photographs.", "Enjoy a relaxed final evening."],
    ]
    for i in range(days):
        lines = ideas[i % len(ideas)].copy()
        if "adventure" in interests:
            lines[1] = "Consider a locally operated outdoor activity, subject to weather and safety conditions."
        if "food" in interests:
            lines[2] = "Try a reputable local food spot and regional specialities."
        day_plans.append((f"Day {i+1}", lines))
    return day_plans

def build_pdf(destination, days, travellers, interests, cost, itinerary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=38, leftMargin=38, topMargin=38, bottomMargin=38)
    styles = getSampleStyleSheet()
    story = [Paragraph("TrekVerse — Travel Plan", styles["Title"]), Spacer(1, 10)]
    story.append(Paragraph(f"<b>Destination:</b> {destination['place']}, {destination['state']}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Duration:</b> {days} days &nbsp;&nbsp; <b>Travellers:</b> {travellers}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Interests:</b> {', '.join(interests) if interests else 'General sightseeing'}", styles["BodyText"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Illustrative budget estimate", styles["Heading2"]))
    rows = [["Expense", "Estimated amount (INR)"], ["Stay", f"₹{cost['stay']:,}"], ["Food", f"₹{cost['food']:,}"], ["Local travel", f"₹{cost['local']:,}"], ["Activities", f"₹{cost['activities']:,}"], ["Intercity travel", f"₹{cost['intercity']:,}"], ["Total", f"₹{cost['total']:,}"]]
    table = Table(rows, colWidths=[250, 180])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#16324F")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.5,colors.grey),("PADDING",(0,0),(-1,-1),7),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]))
    story.append(table)
    story.append(Spacer(1,12))
    story.append(Paragraph("Suggested day-wise plan", styles["Heading2"]))
    for title, lines in itinerary:
        story.append(Paragraph(title, styles["Heading3"]))
        for line in lines:
            story.append(Paragraph("• " + line, styles["BodyText"]))
    story.append(Spacer(1,10))
    story.append(Paragraph("Note: Prices are illustrative planning estimates, not live quotes or guaranteed costs. Verify transport, accommodation, permits, weather and local conditions before travel.", styles["Italic"]))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def assistant_reply(question):
    q = question.lower()
    if any(x in q for x in ["budget","cost","cheap","₹","rupee"]):
        return "Use Discover & Budget to compare estimated group costs. Add your intercity fare separately. Estimates are illustrative and may differ from actual prices."
    if any(x in q for x in ["weather","rain","temperature"]):
        return "Open the Weather tab, choose a destination and load the forecast. Check local advisories before outdoor activities."
    if any(x in q for x in ["pack","packing","carry"]):
        return "Pack ID, medicines, reusable water bottle, comfortable footwear, weather-appropriate layers, chargers, power bank and any destination-specific permits. For high altitude, plan acclimatisation."
    if any(x in q for x in ["map","direction","route","location"]):
        return "Open the Map tab to view approximate destination markers, or use the Google Maps link on a destination card for navigation."
    if any(x in q for x in ["best time","season","when to visit"]):
        return "Check the Best season field on each destination card. Seasons are broad guidance; verify current weather and local closures."
    if any(x in q for x in ["safety","emergency","police"]):
        return "For emergencies in India, call 112. Share your itinerary with someone you trust and follow local authority guidance."
    return "I can help with budget estimates, itinerary ideas, packing, maps, seasons and basic safety tips. Try asking a more specific travel question. This is a rule-based helper, not a live generative AI service."

# Sidebar / common inputs
st.sidebar.title("🧭 TrekVerse")
st.sidebar.caption("Explore India. Plan within your budget.")
st.sidebar.info("Planning estimates only. Verify live prices, availability, permits and local advisories before booking.")
origin = st.sidebar.text_input("Your starting city / state", value="Indore")
budget = st.sidebar.number_input("Total trip budget (₹)", min_value=1000, max_value=10000000, value=15000, step=1000)
travellers = st.sidebar.number_input("Travellers", min_value=1, max_value=30, value=2, step=1)
days = st.sidebar.number_input("Trip duration (days)", min_value=1, max_value=30, value=3, step=1)
selected_interests = st.sidebar.multiselect("Interests", INTERESTS, default=["nature","food"])
travel_fare = st.sidebar.number_input("Intercity fare per person (₹, optional)", min_value=0, max_value=500000, value=0, step=500)

if "saved_places" not in st.session_state:
    st.session_state.saved_places = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🧭 TrekVerse")
st.subheader("Your India travel planner — destinations, budgets, itineraries and maps")
st.caption("V6 • Free planning tools • Estimates are not live booking prices")

tabs = st.tabs([
    "Discover & Budget",
    "Itinerary Studio",
    "Multi-city Route",
    "Map",
    "Weather",
    "Travel Chat",
    "Saved Places",
    "Admin & Data",
    "Trip Toolkit",
])

# TAB 1 — Discover
with tabs[0]:
    st.header("Find destinations that fit your trip")
    matches = rank_destinations(origin, budget, int(days), int(travellers), selected_interests)
    col1, col2, col3 = st.columns(3)
    col1.metric("Destinations in catalogue", len(DESTINATIONS))
    col2.metric("Budget", f"₹{budget:,.0f}")
    col3.metric("Recommended results", len(matches))
    search_text = st.text_input("Search destination or state", key="destination_search")
    filtered = [item for item in matches if not search_text or search_text.lower() in item[2]["place"].lower() or search_text.lower() in item[2]["state"].lower()]
    if not filtered:
        st.warning("No matching destination in the current ranked results. Clear the search or try another term.")
    for score, total, d, c in filtered:
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.subheader(f"{d['place']} · {d['state']}")
                st.write(d["about"])
                st.caption(f"{d['type']}  |  Best season: {d['months']}  |  Tags: {', '.join(d['tags'])}")
                st.link_button("Open on Google Maps", maps_url(d["place"]))
            with right:
                st.metric("Estimated group total", f"₹{c['total']:,}")
                remaining = int(budget - c["total"])
                st.metric("Budget remaining", f"₹{remaining:,}", delta="Within budget" if remaining >= 0 else "Over budget")
                if st.button("♡ Save destination", key="save_" + d["place"]):
                    if d["place"] not in st.session_state.saved_places:
                        st.session_state.saved_places.append(d["place"])
                    st.success("Saved to this browser session.")
    if matches:
        comparison_rows = []
        for _, _, d, c in filtered:
            comparison_rows.append({
                "Destination": d["place"],
                "State": d["state"],
                "Group estimate (₹)": c["total"],
                "Remaining (₹)": budget - c["total"],
                "Best season": d["months"],
            })
        if comparison_rows:
            comparison_df = pd.DataFrame(comparison_rows)
            st.download_button(
                "Download comparison CSV",
                data=comparison_df.to_csv(index=False).encode("utf-8"),
                file_name="trekverse_comparison.csv",
                mime="text/csv",
            )

# TAB 2 — Itinerary
with tabs[1]:
    st.header("Day-wise itinerary studio")
    choices = [d for _, _, d, _ in matches] or DESTINATIONS
    chosen = st.selectbox("Choose destination", [d["place"] for d in choices], key="itinerary_destination")
    destination = next(d for d in DESTINATIONS if d["place"] == chosen)
    itinerary = make_itinerary(destination, int(days), selected_interests)
    itinerary_cost = estimate_cost(destination, int(days), int(travellers), int(travel_fare))
    st.write(f"### {destination['place']}, {destination['state']}")
    st.write(destination["about"])
    for heading, activities in itinerary:
        with st.expander(heading, expanded=True):
            for activity in activities:
                st.write("• " + activity)
    st.subheader("Estimated budget breakdown")
    budget_df = pd.DataFrame([
        {"Expense": "Stay", "Amount (₹)": itinerary_cost["stay"]},
        {"Expense": "Food", "Amount (₹)": itinerary_cost["food"]},
        {"Expense": "Local travel", "Amount (₹)": itinerary_cost["local"]},
        {"Expense": "Activities", "Amount (₹)": itinerary_cost["activities"]},
        {"Expense": "Intercity travel", "Amount (₹)": itinerary_cost["intercity"]},
    ])
    st.dataframe(budget_df, use_container_width=True, hide_index=True)
    st.metric("Estimated total", f"₹{itinerary_cost['total']:,}")
    st.download_button("Download itinerary CSV", budget_df.to_csv(index=False).encode("utf-8"), "trekverse_itinerary_budget.csv", "text/csv")
    pdf_bytes = build_pdf(destination, int(days), int(travellers), selected_interests, itinerary_cost, itinerary)
    st.download_button("Download travel booklet (PDF)", pdf_bytes, "trekverse_travel_plan.pdf", "application/pdf")

# TAB 3 — Multi-city
with tabs[2]:
    st.header("Multi-city trip cost estimator")
    st.warning("This tool adds estimated costs for selected stops. It does not optimise route order or calculate live directions/fares.")
    city_names = [d["place"] for d in DESTINATIONS]
    selected_cities = st.multiselect("Choose destinations / stops", city_names, default=["Indore","Ujjain"])
    city_days = st.number_input("Days per stop", min_value=1, max_value=15, value=2, key="multi_days")
    if selected_cities:
        route_rows = []
        route_total = 0
        for city in selected_cities:
            d = next(x for x in DESTINATIONS if x["place"] == city)
            c = estimate_cost(d, int(city_days), int(travellers))
            route_total += c["total"]
            route_rows.append({"Stop": city, "State": d["state"], "Days": city_days, "Estimated cost (₹)": c["total"]})
        route_df = pd.DataFrame(route_rows)
        st.dataframe(route_df, use_container_width=True, hide_index=True)
        st.metric("Estimated total for selected stops", f"₹{route_total:,}")
        st.download_button("Download multi-city estimate CSV", route_df.to_csv(index=False).encode("utf-8"), "trekverse_multi_city.csv", "text/csv")
    else:
        st.info("Choose at least one stop to calculate an estimate.")

# TAB 4 — Map
with tabs[3]:
    st.header("Explore destinations on the map")
    map_region = st.selectbox("Filter region", ["All regions"] + sorted({d["region"] for d in DESTINATIONS}))
    map_data = [d for d in DESTINATIONS if map_region == "All regions" or d["region"] == map_region]
    m = folium.Map(location=[22.5, 79.0], zoom_start=5, tiles="OpenStreetMap")
    for d in map_data:
        folium.Marker(
            [d["lat"], d["lon"]],
            tooltip=d["place"],
            popup=f"<b>{d['place']}</b><br>{d['state']}<br>{d['type']}",
        ).add_to(m)
    st_folium(m, use_container_width=True, height=520, returned_objects=[])
    st.caption("Map markers show approximate destination centres, not exact hotels, attractions or route paths.")

# TAB 5 — Weather
with tabs[4]:
    st.header("Weather forecast")
    weather_place = st.selectbox("Choose destination", [d["place"] for d in DESTINATIONS], key="weather_destination")
    wd = next(d for d in DESTINATIONS if d["place"] == weather_place)
    if st.button("Load current weather and 7-day forecast"):
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": wd["lat"],
                "longitude": wd["lon"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 7,
            }
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            weather = response.json()
            current = weather.get("current", {})
            a, b, c = st.columns(3)
            a.metric("Temperature", f"{current.get('temperature_2m','—')} °C")
            b.metric("Feels like", f"{current.get('apparent_temperature','—')} °C")
            c.metric("Wind speed", f"{current.get('wind_speed_10m','—')} km/h")
            daily = weather.get("daily", {})
            forecast_df = pd.DataFrame({
                "Date": daily.get("time", []),
                "Min °C": daily.get("temperature_2m_min", []),
                "Max °C": daily.get("temperature_2m_max", []),
                "Rain chance %": daily.get("precipitation_probability_max", []),
                "Weather code": daily.get("weather_code", []),
            })
            st.dataframe(forecast_df, use_container_width=True, hide_index=True)
            st.caption("Weather data supplied by Open-Meteo. Forecasts can change; verify before travel.")
        except Exception as exc:
            st.error(f"Weather could not be loaded. Check your internet connection and try again. Details: {exc}")

# TAB 6 — Travel Chat
with tabs[5]:
    st.header("TrekVerse travel helper")
    st.caption("Rule-based assistant: it does not call a generative AI model.")
    for entry in st.session_state.chat_history:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])
    prompt = st.chat_input("Ask about budgets, packing, seasons, maps or safety...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        answer = assistant_reply(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

# TAB 7 — Saved
with tabs[6]:
    st.header("Saved destinations")
    st.caption("Saved places remain in this browser session only; they are not stored in a cloud account.")
    if st.session_state.saved_places:
        for place in st.session_state.saved_places:
            d = next((x for x in DESTINATIONS if x["place"] == place), None)
            if d:
                st.write(f"**{d['place']}**, {d['state']} — {d['type']}")
                st.link_button("Open map", maps_url(d["place"]), key="saved_map_" + d["place"])
        if st.button("Clear saved places"):
            st.session_state.saved_places = []
            st.rerun()
    else:
        st.info("You have not saved any destinations yet. Use the Save destination button in Discover & Budget.")

# TAB 8 — Admin / Data
with tabs[7]:
    st.header("Destination data")
    st.write(f"Current built-in catalogue: **{len(DESTINATIONS)} destinations**.")
    data_df = pd.DataFrame(DESTINATIONS)
    st.dataframe(data_df[["place","state","region","type","months","daily","stay"]], use_container_width=True, hide_index=True)
    st.download_button("Download destination catalogue CSV", data_df.to_csv(index=False).encode("utf-8"), "trekverse_destinations.csv", "text/csv")
    uploaded = st.file_uploader("Preview an alternative destination CSV (does not change the built-in catalogue)", type=["csv"])
    if uploaded is not None:
        try:
            preview_df = pd.read_csv(uploaded)
            st.success("CSV loaded for preview only.")
            st.dataframe(preview_df.head(100), use_container_width=True)
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")
    st.caption("There is no admin login or persistent database in this version. Uploaded CSV files are preview-only.")

# TAB 9 — Toolkit
with tabs[8]:
    st.header("Trip toolkit")
    st.subheader("Packing checklist")
    checklist_items = [
        "Government ID and booking confirmations",
        "Phone, charger and power bank",
        "Reusable water bottle",
        "Comfortable walking shoes",
        "Weather-appropriate clothes",
        "Personal medicines and basic first aid",
        "Cash, cards and emergency contacts",
        "Sun protection and personal hygiene items",
        "Destination-specific permits / documents",
    ]
    for item in checklist_items:
        st.checkbox(item, key="check_" + item)
    st.divider()
    st.subheader("Useful travel links")
    link_cols = st.columns(3)
    links = [
        ("IRCTC train booking","https://www.irctc.co.in/"),
        ("redBus","https://www.redbus.in/"),
        ("Google Flights","https://www.google.com/travel/flights"),
        ("Google Hotels","https://www.google.com/travel/hotels"),
        ("Incredible India","https://www.incredibleindia.gov.in/"),
        ("Google Maps","https://maps.google.com/"),
    ]
    for i, (label, url) in enumerate(links):
        with link_cols[i % 3]:
            st.link_button(label, url)
    st.info("India emergency response number: **112**. For immediate emergencies, contact local authorities.")
    st.caption("External links are shortcuts only. TrekVerse does not book tickets, hotels or activities.")
