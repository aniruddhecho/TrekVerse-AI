import streamlit as st
import pandas as pd
import re
import requests
from urllib.parse import quote_plus
import folium
from streamlit_folium import st_folium
from calendar import month_name

st.set_page_config(page_title="TrekVerse | India Budget Travel", page_icon="🧭", layout="wide")

# Broad India destination starter database.
# Costs are illustrative per-person PER DAY estimates in INR, not live quotes.
# Intercity transport is entered by the user because fares depend on origin, date and mode.
DESTINATIONS = [
    # North
    {"place":"Amritsar","state":"Punjab","region":"North","stay":700,"food":500,"local":250,"activities":200,"tags":["Historical","Food","Culture"],"months":"October–March","highlights":["Golden Temple","Jallianwala Bagh","Wagah border ceremony"]},
    {"place":"Chandigarh","state":"Chandigarh","region":"North","stay":900,"food":600,"local":350,"activities":250,"tags":["Nature","Architecture","Food"],"months":"October–March","highlights":["Rock Garden","Sukhna Lake","Capitol Complex"]},
    {"place":"Shimla","state":"Himachal Pradesh","region":"North","stay":1000,"food":650,"local":450,"activities":300,"tags":["Nature","Adventure","Snow"],"months":"March–June; December–February for snow","highlights":["The Ridge","Mall Road","Kufri"]},
    {"place":"Manali","state":"Himachal Pradesh","region":"North","stay":1100,"food":650,"local":500,"activities":450,"tags":["Nature","Adventure","Snow"],"months":"March–June; December–February for snow","highlights":["Old Manali","Hadimba Temple","Solang Valley"]},
    {"place":"Dharamshala and McLeod Ganj","state":"Himachal Pradesh","region":"North","stay":900,"food":600,"local":350,"activities":250,"tags":["Nature","Adventure","Culture"],"months":"March–June; September–November","highlights":["Bhagsu Waterfall","Dalai Lama Temple","Triund trail"]},
    {"place":"Kasol","state":"Himachal Pradesh","region":"North","stay":800,"food":550,"local":300,"activities":250,"tags":["Nature","Adventure"],"months":"March–June; September–November","highlights":["Parvati River","Chalal walk","Tosh village"]},
    {"place":"Rishikesh","state":"Uttarakhand","region":"North","stay":700,"food":500,"local":300,"activities":500,"tags":["Nature","Adventure","Spiritual"],"months":"September–April","highlights":["Ganga aarti","Ram Jhula","River rafting (seasonal)"]},
    {"place":"Haridwar","state":"Uttarakhand","region":"North","stay":650,"food":450,"local":250,"activities":150,"tags":["Spiritual","Historical","Culture"],"months":"October–March","highlights":["Har Ki Pauri","Mansa Devi Temple","Ganga aarti"]},
    {"place":"Nainital","state":"Uttarakhand","region":"North","stay":900,"food":550,"local":350,"activities":300,"tags":["Nature","Adventure"],"months":"March–June; September–November","highlights":["Naini Lake","Snow View Point","Mall Road"]},
    {"place":"Jaipur","state":"Rajasthan","region":"North","stay":800,"food":550,"local":300,"activities":350,"tags":["Historical","Food","Shopping","Architecture"],"months":"October–March","highlights":["Amber Fort","Hawa Mahal","City Palace"]},
    {"place":"Udaipur","state":"Rajasthan","region":"North","stay":1000,"food":650,"local":350,"activities":350,"tags":["Historical","Nature","Food","Culture"],"months":"October–March","highlights":["Lake Pichola","City Palace","Bagore Ki Haveli"]},
    {"place":"Jodhpur","state":"Rajasthan","region":"North","stay":800,"food":550,"local":300,"activities":300,"tags":["Historical","Food","Shopping"],"months":"October–March","highlights":["Mehrangarh Fort","Blue City lanes","Jaswant Thada"]},
    {"place":"Jaisalmer","state":"Rajasthan","region":"North","stay":900,"food":600,"local":350,"activities":600,"tags":["Historical","Adventure","Culture"],"months":"October–March","highlights":["Jaisalmer Fort","Sam Sand Dunes","Patwon Ki Haveli"]},
    {"place":"Pushkar","state":"Rajasthan","region":"North","stay":700,"food":500,"local":250,"activities":200,"tags":["Spiritual","Historical","Shopping"],"months":"October–March","highlights":["Pushkar Lake","Brahma Temple","Local bazaar"]},
    "PLACEHOLDER",
    # Central
    {"place":"Ujjain","state":"Madhya Pradesh","region":"Central","stay":650,"food":450,"local":250,"activities":200,"tags":["Spiritual","Historical","Food"],"months":"October–March","highlights":["Mahakaleshwar Temple","Ram Ghat","Kal Bhairav Temple"]},
    {"place":"Mandu","state":"Madhya Pradesh","region":"Central","stay":700,"food":450,"local":300,"activities":250,"tags":["Nature","Historical","Architecture"],"months":"July–February","highlights":["Jahaz Mahal","Hindola Mahal","Rani Roopmati Pavilion"]},
    {"place":"Maheshwar","state":"Madhya Pradesh","region":"Central","stay":750,"food":500,"local":250,"activities":200,"tags":["Nature","Historical","Shopping","Culture"],"months":"October–March","highlights":["Ahilya Fort","Narmada ghats","Maheshwari handloom"]},
    {"place":"Bhopal","state":"Madhya Pradesh","region":"Central","stay":750,"food":500,"local":300,"activities":250,"tags":["Nature","Historical","Food"],"months":"October–March","highlights":["Upper Lake","Tribal Museum","Sanchi day trip"]},
    {"place":"Pachmarhi","state":"Madhya Pradesh","region":"Central","stay":1000,"food":550,"local":550,"activities":350,"tags":["Nature","Adventure"],"months":"October–June","highlights":["Bee Falls","Dhoopgarh","Pandav Caves"]},
    {"place":"Khajuraho","state":"Madhya Pradesh","region":"Central","stay":800,"food":500,"local":250,"activities":350,"tags":["Historical","Architecture","Culture"],"months":"October–March","highlights":["Western Group of Temples","Eastern temples","Raneh Falls"]},
    {"place":"Orchha","state":"Madhya Pradesh","region":"Central","stay":650,"food":450,"local":200,"activities":200,"tags":["Historical","Nature","Architecture"],"months":"October–March","highlights":["Orchha Fort complex","Chaturbhuj Temple","Betwa River"]},
    {"place":"Varanasi","state":"Uttar Pradesh","region":"Central","stay":750,"food":550,"local":300,"activities":250,"tags":["Spiritual","Historical","Food","Culture"],"months":"October–March","highlights":["Dashashwamedh Ghat","Kashi Vishwanath Temple","Sarnath"]},
    {"place":"Agra","state":"Uttar Pradesh","region":"Central","stay":800,"food":550,"local":300,"activities":450,"tags":["Historical","Architecture","Food"],"months":"October–March","highlights":["Taj Mahal","Agra Fort","Fatehpur Sikri"]},
    {"place":"Lucknow","state":"Uttar Pradesh","region":"Central","stay":800,"food":650,"local":300,"activities":250,"tags":["Historical","Food","Architecture"],"months":"October–March","highlights":["Bara Imambara","Rumi Darwaza","Awadhi food trail"]},
    "PLACEHOLDER",
    # West
    {"place":"Mumbai","state":"Maharashtra","region":"West","stay":1300,"food":750,"local":450,"activities":350,"tags":["Food","Historical","Shopping","Nature"],"months":"November–February","highlights":["Gateway of India","Marine Drive","Elephanta Caves"]},
    {"place":"Pune","state":"Maharashtra","region":"West","stay":900,"food":650,"local":350,"activities":250,"tags":["Historical","Food","Nature"],"months":"October–February","highlights":["Shaniwar Wada","Aga Khan Palace","Sinhagad Fort"]},
    {"place":"Nashik","state":"Maharashtra","region":"West","stay":850,"food":550,"local":350,"activities":250,"tags":["Nature","Spiritual","Food"],"months":"October–March","highlights":["Trimbakeshwar","Pandavleni Caves","Godavari ghats"]},
    {"place":"Mahabaleshwar","state":"Maharashtra","region":"West","stay":1100,"food":600,"local":450,"activities":350,"tags":["Nature","Adventure"],"months":"October–June","highlights":["Venna Lake","Arthur's Seat","Mapro Garden"]},
    {"place":"Goa","state":"Goa","region":"West","stay":1200,"food":700,"local":500,"activities":450,"tags":["Nature","Food","Adventure","Shopping"],"months":"November–February","highlights":["Beaches","Old Goa churches","Local markets"]},
    {"place":"Ahmedabad","state":"Gujarat","region":"West","stay":800,"food":550,"local":300,"activities":250,"tags":["Historical","Food","Shopping","Architecture"],"months":"November–February","highlights":["Sabarmati Ashram","Adalaj Stepwell","Old city heritage walk"]},
    {"place":"Rann of Kutch","state":"Gujarat","region":"West","stay":1400,"food":650,"local":650,"activities":500,"tags":["Nature","Culture","Photography"],"months":"November–February","highlights":["White Rann","Kala Dungar","Craft villages"]},
    {"place":"Diu","state":"Dadra and Nagar Haveli and Daman and Diu","region":"West","stay":900,"food":550,"local":300,"activities":250,"tags":["Nature","Historical","Food"],"months":"October–March","highlights":["Diu Fort","Nagoa Beach","Naida Caves"]},
    "PLACEHOLDER",
    # South
    {"place":"Hyderabad","state":"Telangana","region":"South","stay":900,"food":650,"local":350,"activities":350,"tags":["Historical","Food","Shopping","Architecture"],"months":"October–February","highlights":["Charminar","Golconda Fort","Hussain Sagar"]},
    {"place":"Hampi","state":"Karnataka","region":"South","stay":800,"food":550,"local":350,"activities":300,"tags":["Historical","Nature","Adventure","Architecture"],"months":"October–February","highlights":["Virupaksha Temple","Vittala Temple","Hampi bazaar"]},
    {"place":"Bengaluru","state":"Karnataka","region":"South","stay":1100,"food":750,"local":400,"activities":300,"tags":["Food","Nature","Shopping"],"months":"October–February","highlights":["Lalbagh","Cubbon Park","Bengaluru food streets"]},
    {"place":"Mysuru","state":"Karnataka","region":"South","stay":850,"food":600,"local":300,"activities":300,"tags":["Historical","Culture","Food","Architecture"],"months":"October–March","highlights":["Mysore Palace","Chamundi Hills","Devaraja Market"]},
    {"place":"Coorg","state":"Karnataka","region":"South","stay":1100,"food":650,"local":500,"activities":350,"tags":["Nature","Adventure"],"months":"October–March","highlights":["Abbey Falls","Raja's Seat","Coffee estates"]},
    {"place":"Gokarna","state":"Karnataka","region":"South","stay":900,"food":550,"local":350,"activities":250,"tags":["Nature","Adventure"],"months":"October–March","highlights":["Om Beach","Kudle Beach","Coastal trail"]},
    {"place":"Chennai","state":"Tamil Nadu","region":"South","stay":1000,"food":650,"local":400,"activities":300,"tags":["Food","Historical","Culture"],"months":"November–February","highlights":["Marina Beach","Kapaleeshwarar Temple","Fort St. George"]},
    {"place":"Ooty","state":"Tamil Nadu","region":"South","stay":1100,"food":600,"local":450,"activities":350,"tags":["Nature","Adventure"],"months":"October–June","highlights":["Botanical Gardens","Ooty Lake","Nilgiri Mountain Railway"]},
    {"place":"Kodaikanal","state":"Tamil Nadu","region":"South","stay":1000,"food":600,"local":450,"activities":300,"tags":["Nature","Adventure"],"months":"October–June","highlights":["Kodaikanal Lake","Coaker's Walk","Pillar Rocks"]},
    {"place":"Madurai","state":"Tamil Nadu","region":"South","stay":750,"food":550,"local":250,"activities":250,"tags":["Spiritual","Historical","Food","Architecture"],"months":"October–March","highlights":["Meenakshi Amman Temple","Thirumalai Nayakkar Palace","Local food streets"]},
    {"place":"Rameswaram","state":"Tamil Nadu","region":"South","stay":800,"food":550,"local":300,"activities":250,"tags":["Spiritual","Nature","Historical"],"months":"October–April","highlights":["Ramanathaswamy Temple","Pamban Bridge","Dhanushkodi"]},
    {"place":"Kochi","state":"Kerala","region":"South","stay":1000,"food":650,"local":350,"activities":300,"tags":["Historical","Food","Culture","Nature"],"months":"October–March","highlights":["Fort Kochi","Chinese fishing nets","Mattancherry Palace"]},
    {"place":"Munnar","state":"Kerala","region":"South","stay":1200,"food":650,"local":500,"activities":350,"tags":["Nature","Adventure"],"months":"September–March","highlights":["Tea gardens","Eravikulam National Park","Mattupetty Dam"]},
    {"place":"Alappuzha","state":"Kerala","region":"South","stay":1000,"food":650,"local":350,"activities":450,"tags":["Nature","Food"],"months":"November–February","highlights":["Backwaters","Alappuzha Beach","Village canoe trip"]},
    {"place":"Varkala","state":"Kerala","region":"South","stay":1000,"food":650,"local":350,"activities":300,"tags":["Nature","Adventure","Food"],"months":"October–March","highlights":["Varkala cliff","Papanasam Beach","Janardhana Swamy Temple"]},
    {"place":"Puducherry","state":"Puducherry","region":"South","stay":1000,"food":700,"local":350,"activities":300,"tags":["Nature","Food","Historical","Culture"],"months":"October–March","highlights":["White Town","Promenade Beach","Auroville"]},
    "PLACEHOLDER",
    # East and Northeast
    {"place":"Kolkata","state":"West Bengal","region":"East","stay":850,"food":600,"local":300,"activities":300,"tags":["Historical","Food","Culture","Architecture"],"months":"October–February","highlights":["Victoria Memorial","Howrah Bridge","College Street"]},
    {"place":"Darjeeling","state":"West Bengal","region":"East","stay":1100,"food":650,"local":450,"activities":350,"tags":["Nature","Adventure"],"months":"March–May; October–November","highlights":["Tiger Hill","Tea gardens","Darjeeling Himalayan Railway"]},
    {"place":"Gangtok","state":"Sikkim","region":"East","stay":1100,"food":650,"local":450,"activities":350,"tags":["Nature","Adventure","Culture"],"months":"March–June; September–November","highlights":["MG Marg","Tsomgo Lake","Rumtek Monastery"]},
    {"place":"Shillong","state":"Meghalaya","region":"East","stay":1000,"food":600,"local":450,"activities":350,"tags":["Nature","Adventure","Food"],"months":"October–April","highlights":["Umiam Lake","Elephant Falls","Laitlum Canyon"]},
    {"place":"Cherrapunji (Sohra)","state":"Meghalaya","region":"East","stay":1000,"food":600,"local":550,"activities":400,"tags":["Nature","Adventure"],"months":"October–May","highlights":["Nohkalikai Falls","Mawsmai Cave","Living root bridges"]},
    {"place":"Kaziranga","state":"Assam","region":"East","stay":1200,"food":650,"local":600,"activities":900,"tags":["Nature","Adventure","Wildlife"],"months":"November–April","highlights":["Kaziranga safari","Orchid park","Brahmaputra river"]},
    {"place":"Guwahati","state":"Assam","region":"East","stay":850,"food":550,"local":300,"activities":250,"tags":["Spiritual","Nature","Food"],"months":"October–April","highlights":["Kamakhya Temple","Brahmaputra riverfront","Umananda Island"]},
    {"place":"Tawang","state":"Arunachal Pradesh","region":"East","stay":1300,"food":650,"local":700,"activities":350,"tags":["Nature","Adventure","Snow","Culture"],"months":"April–October; winter conditions can be severe","highlights":["Tawang Monastery","Sela Pass","Madhuri Lake"]},
    {"place":"Puri","state":"Odisha","region":"East","stay":800,"food":550,"local":300,"activities":250,"tags":["Spiritual","Nature","Food"],"months":"October–February","highlights":["Jagannath Temple","Puri Beach","Konark Sun Temple"]},
    {"place":"Bhubaneswar","state":"Odisha","region":"East","stay":800,"food":550,"local":300,"activities":250,"tags":["Historical","Architecture","Food"],"months":"October–February","highlights":["Lingaraj Temple","Udayagiri and Khandagiri Caves","Dhauli"]},
    {"place":"Ranchi","state":"Jharkhand","region":"East","stay":750,"food":500,"local":350,"activities":250,"tags":["Nature","Adventure"],"months":"October–March","highlights":["Hundru Falls","Dassam Falls","Rock Garden"]},
    {"place":"Raipur","state":"Chhattisgarh","region":"Central","stay":800,"food":550,"local":350,"activities":250,"tags":["Food","Nature","Culture"],"months":"October–March","highlights":["Nandan Van","Purkhouti Muktangan","Sirpur day trip"]},
    {"place":"Visakhapatnam","state":"Andhra Pradesh","region":"South","stay":900,"food":600,"local":350,"activities":300,"tags":["Nature","Food","Adventure"],"months":"October–March","highlights":["RK Beach","Kailasagiri","Submarine Museum"]},
    {"place":"Araku Valley","state":"Andhra Pradesh","region":"South","stay":900,"food":550,"local":500,"activities":300,"tags":["Nature","Adventure"],"months":"October–March","highlights":["Borra Caves","Coffee plantations","Araku viewpoints"]},
    {"place":"Port Blair (Sri Vijaya Puram)","state":"Andaman and Nicobar Islands","region":"Islands","stay":1500,"food":800,"local":600,"activities":900,"tags":["Nature","Adventure","History"],"months":"November–April","highlights":["Cellular Jail","Corbyn's Cove","Ross Island boat trip"]},
    {"place":"Srinagar","state":"Jammu and Kashmir","region":"North","stay":1300,"food":700,"local":500,"activities":500,"tags":["Nature","Adventure","Snow"],"months":"April–October; winter for snow","highlights":["Dal Lake","Mughal Gardens","Old Srinagar"]},
    {"place":"Leh","state":"Ladakh","region":"North","stay":1500,"food":750,"local":700,"activities":600,"tags":["Nature","Adventure","Snow"],"months":"May–September","highlights":["Leh Palace","Shanti Stupa","Nubra Valley (permit/route dependent)"]},
    {"place":"Kargil","state":"Ladakh","region":"North","stay":1100,"food":650,"local":600,"activities":300,"tags":["Nature","Historical","Adventure"],"months":"May–September","highlights":["Kargil War Memorial","Sur Valley","Local heritage sites"]},
]

DESTINATIONS = [d for d in DESTINATIONS if isinstance(d, dict)]
MONTHS = list(month_name)[1:]
INTERESTS = sorted({tag for d in DESTINATIONS for tag in d["tags"]})

# Approximate map coordinates for destination markers. Confirm exact pins before navigation.
COORDS = {
    "Amritsar":(31.6340,74.8723),"Chandigarh":(30.7333,76.7794),"Shimla":(31.1048,77.1734),
    "Manali":(32.2432,77.1892),"Dharamshala and McLeod Ganj":(32.2190,76.3234),"Kasol":(32.0100,77.3150),
    "Rishikesh":(30.0869,78.2676),"Haridwar":(29.9457,78.1642),"Nainital":(29.3803,79.4636),
    "Jaipur":(26.9124,75.7873),"Udaipur":(24.5854,73.7125),"Jodhpur":(26.2389,73.0243),
    "Jaisalmer":(26.9157,70.9083),"Pushkar":(26.4899,74.5511),"Ujjain":(23.1793,75.7849),
    "Mandu":(22.3333,75.4000),"Maheshwar":(22.1759,75.5870),"Bhopal":(23.2599,77.4126),
    "Pachmarhi":(22.4674,78.4330),"Khajuraho":(24.8318,79.9199),"Orchha":(25.3519,78.6407),
    "Varanasi":(25.3176,82.9739),"Agra":(27.1767,78.0081),"Lucknow":(26.8467,80.9462),
    "Mumbai":(19.0760,72.8777),"Pune":(18.5204,73.8567),"Nashik":(19.9975,73.7898),
    "Mahabaleshwar":(17.9307,73.6477),"Goa":(15.2993,74.1240),"Ahmedabad":(23.0225,72.5714),
    "Rann of Kutch":(23.7337,69.8597),"Diu":(20.7141,70.9874),"Hyderabad":(17.3850,78.4867),
    "Hampi":(15.3350,76.4600),"Bengaluru":(12.9716,77.5946),"Mysuru":(12.2958,76.6394),
    "Coorg":(12.3375,75.8069),"Gokarna":(14.5479,74.3188),"Chennai":(13.0827,80.2707),
    "Ooty":(11.4064,76.6932),"Kodaikanal":(10.2381,77.4892),"Madurai":(9.9252,78.1198),
    "Rameswaram":(9.2876,79.3129),"Kochi":(9.9312,76.2673),"Munnar":(10.0889,77.0595),
    "Alappuzha":(9.4981,76.3388),"Varkala":(8.7379,76.7163),"Puducherry":(11.9416,79.8083),
    "Kolkata":(22.5726,88.3639),"Darjeeling":(27.0410,88.2663),"Gangtok":(27.3389,88.6065),
    "Shillong":(25.5788,91.8933),"Cherrapunji (Sohra)":(25.2702,91.7323),"Kaziranga":(26.5775,93.1711),
    "Guwahati":(26.1445,91.7362),"Tawang":(27.5860,91.8594),"Puri":(19.8135,85.8312),
    "Bhubaneswar":(20.2961,85.8245),"Ranchi":(23.3441,85.3096),"Raipur":(21.2514,81.6296),
    "Visakhapatnam":(17.6868,83.2185),"Araku Valley":(18.3273,82.8775),
    "Port Blair (Sri Vijaya Puram)":(11.6234,92.7265),"Srinagar":(34.0837,74.7973),
    "Leh":(34.1526,77.5771),"Kargil":(34.5539,76.1349)
}

def fetch_weather(place):
    """Fetch a 7-day forecast from the free Open-Meteo API; no API key required."""
    coords = COORDS.get(place)
    if not coords:
        return None, "No map/weather coordinates are available for this destination yet."
    lat, lon = coords
    endpoint = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto", "forecast_days": 7
    }
    try:
        response = requests.get(endpoint, params=params, timeout=12)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException:
        return None, "Weather could not be loaded. Check the internet connection and try again."

def weather_description(code):
    descriptions = {
        0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
        45:"Fog",48:"Depositing rime fog",51:"Light drizzle",53:"Drizzle",
        55:"Dense drizzle",61:"Slight rain",63:"Rain",65:"Heavy rain",
        71:"Slight snow",73:"Snow",75:"Heavy snow",80:"Rain showers",
        81:"Rain showers",82:"Violent rain showers",95:"Thunderstorm",
        96:"Thunderstorm with hail",99:"Thunderstorm with heavy hail"
    }
    return descriptions.get(code, "Variable conditions")

def google_maps_search(place):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(place + ", India")


st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#071b2b 0%,#102f3d 55%,#173b42 100%); color:#f4f7f8;}
h1,h2,h3,p,label {color:#f4f7f8 !important;}
.block-container {max-width:1150px; padding-top:2rem;}
.hero {padding:24px 28px; border:1px solid #42616a; border-radius:18px; background:rgba(255,255,255,.06); margin-bottom:20px;}
div.stButton > button {background:#12a9ce;color:white;border:0;border-radius:9px;font-weight:600;}
.note {padding:12px 16px;border-left:4px solid #12a9ce;background:rgba(255,255,255,.07);border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero">', unsafe_allow_html=True)
st.title("🧭 TrekVerse V5 — Complete India Travel Companion")
st.write("Find destinations across India, compare estimated costs and generate a downloadable day-wise travel itinerary.")
st.caption("Free V5 • India-wide planner • Chat assistant • Itineraries • Interactive map • Live weather • Travel shortcuts • Checklist")
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Plan your trip")
    origin = st.text_input("Starting city", "Indore")
    budget = st.number_input("Total group budget (₹)", min_value=500, max_value=1000000, value=5000, step=500)
    travellers = st.number_input("Number of travellers", min_value=1, max_value=30, value=1)
    days = st.slider("Number of days", 1, 21, 2)
    month = st.selectbox("Travel month", MONTHS, index=10)
    interests = st.multiselect("Interests", INTERESTS, default=["Nature","Historical"])
    transport_pp = st.number_input("Your estimated round-trip transport cost per person (₹)", min_value=0, max_value=200000, value=0, step=250,
                                   help="Enter the train/bus/flight return fare from your starting city. Set 0 if you want to compare destination costs before adding transport.")
    style = st.selectbox("Travel style", ["Budget","Comfortable"], index=0)
    region_filter = st.multiselect("Regions to explore", ["North","Central","West","South","East","Islands"], default=["North","Central","West","South","East","Islands"])
    find = st.button("Find destinations", use_container_width=True)

per_person_budget = budget / travellers
st.subheader("Your trip snapshot")
a,b,c,d = st.columns(4)
a.metric("Total budget", f"₹{budget:,.0f}")
b.metric("Travellers", int(travellers))
c.metric("Days", int(days))
d.metric("Budget per person", f"₹{per_person_budget:,.0f}")

st.markdown('<div class="note">Transport is not guessed from your starting city. Enter a round-trip fare above (per person) after checking a train, bus or flight. Destination costs below are broad planning estimates, not current quotes.</div>', unsafe_allow_html=True)


matches = []
for p in DESTINATIONS:
    if p["region"] not in region_filter:
        continue
    multiplier = 1.35 if style == "Comfortable" else 1.0
    stay = round(p["stay"] * days * multiplier)
    food = round(p["food"] * days * (1.15 if style == "Comfortable" else 1.0))
    local = round(p["local"] * days)
    activities = round(p["activities"] * days)
    transport = int(transport_pp) * int(travellers)
    destination_cost_group = (stay + food + local + activities) * int(travellers)
    total_group = destination_cost_group + transport
    if total_group > budget:
        continue
    interest_score = len(set(interests).intersection(p["tags"]))
    score = interest_score * 4 + (2 if total_group <= budget * .75 else 0)
    if not interests:
        score += 1
    matches.append({**p,"stay_group":stay*int(travellers),"food_group":food*int(travellers),
                    "local_group":local*int(travellers),"activities_group":activities*int(travellers),
                    "transport_group":transport,"total_group":total_group,
                    "remaining":budget-total_group,"score":score})

matches.sort(key=lambda x:(x["score"],-x["total_group"]), reverse=True)
st.subheader(f"Destinations within budget ({len(matches)} matches)")
if not matches:
    st.warning("No listed destination fits the current inputs. Try increasing the budget, reducing days or travellers, or entering a lower checked transport fare.")
else:
    for p in matches[:12]:
        with st.expander(f"📍 {p['place']}, {p['state']} — estimated group total ₹{p['total_group']:,}"):
            st.write(f"**Region:** {p['region']}  |  **General best season:** {p['months']}")
            st.write(f"**Highlights:** {', '.join(p['highlights'])}")
            st.write(f"**Interests:** {', '.join(p['tags'])}")
            x1,x2,x3,x4,x5 = st.columns(5)
            x1.metric("Stay",f"₹{p['stay_group']:,}")
            x2.metric("Food",f"₹{p['food_group']:,}")
            x3.metric("Local travel",f"₹{p['local_group']:,}")
            x4.metric("Activities",f"₹{p['activities_group']:,}")
            x5.metric("Intercity travel",f"₹{p['transport_group']:,}")
            st.success(f"Estimated remaining budget: ₹{p['remaining']:,}")
            st.caption("See the detailed itinerary builder below to create a schedule for your chosen destination.")

if matches:
    export = pd.DataFrame([{
        "Destination":p["place"],"State/UT":p["state"],"Region":p["region"],
        "Estimated group total (INR)":p["total_group"],"Stay":p["stay_group"],
        "Food":p["food_group"],"Local transport":p["local_group"],
        "Activities":p["activities_group"],"Intercity transport":p["transport_group"],
        "Budget remaining":p["remaining"],"General best season":p["months"]
    } for p in matches])
    st.download_button("⬇️ Download all matching destinations (CSV)", export.to_csv(index=False).encode("utf-8"),
                       file_name="trekverse_india_recommendations.csv", mime="text/csv")

st.divider()
st.header("🗓️ V3 — Build your day-wise travel itinerary")
st.write("Choose one destination from the places that fit your budget. TrekVerse will arrange its listed highlights into a practical sample schedule.")

if matches:
    place_names = [f"{p['place']}, {p['state']}" for p in matches]
    selected_label = st.selectbox("Choose your destination for the itinerary", place_names)
    selected = matches[place_names.index(selected_label)]

    cuisine_ideas = {
        "Punjab": "Punjabi thali, chole kulche or dal with roti",
        "Himachal Pradesh": "Local dham-style meal, siddu where available, or simple thali",
        "Uttarakhand": "Pahadi thali, mandua roti or local seasonal dishes",
        "Rajasthan": "Dal baati churma, gatte ki sabzi or a simple Rajasthani thali",
        "Madhya Pradesh": "Poha-jalebi, dal bafla or a local thali",
        "Uttar Pradesh": "Regional thali, chaat or local vegetarian/non-vegetarian specialties",
        "Maharashtra": "Misal pav, poha or a Maharashtrian thali",
        "Goa": "Goan fish curry/rice or local vegetarian thali",
        "Gujarat": "Gujarati thali, khichdi-kadhi or dhokla",
        "Telangana": "Hyderabadi biryani or a local vegetarian thali",
        "Karnataka": "South Indian meals, dosa or a Karnataka-style thali",
        "Tamil Nadu": "Idli, dosa, meals on a banana leaf or local tiffin",
        "Kerala": "Kerala meals, appam with stew or puttu and kadala",
        "Puducherry": "South Indian meals and French-influenced bakery options",
        "West Bengal": "Bengali thali, fish curry where preferred, or sweets",
        "Sikkim": "Momos, thukpa or a local rice-and-vegetable meal",
        "Meghalaya": "Local Khasi/Garo dishes or simple rice-based meals",
        "Assam": "Assamese thali, rice with seasonal vegetables or fish",
        "Arunachal Pradesh": "Local rice-based dishes and momos where available",
        "Odisha": "Odia thali, dalma or local snacks",
        "Jharkhand": "Local thali, litti-chokha or seasonal tribal cuisine",
        "Chhattisgarh": "Chhattisgarhi thali and local rice-based dishes",
        "Andhra Pradesh": "Andhra meals, pesarattu or local thali",
        "Andaman and Nicobar Islands": "Seafood where preferred or a local Indian thali",
        "Jammu and Kashmir": "Kashmiri wazwan-style dishes or a simple local meal",
        "Ladakh": "Thukpa, skyu or momos"
    }
    cuisine = cuisine_ideas.get(selected["state"], "A local thali or regional specialty from a clean, well-reviewed eatery")
    highlights = selected["highlights"]
    daily_food_group = round(selected["food"] * (1.15 if style == "Comfortable" else 1.0) * travellers)
    daily_stay_group = round(selected["stay"] * (1.35 if style == "Comfortable" else 1.0) * travellers)
    daily_local_group = round(selected["local"] * travellers)
    daily_activity_group = round(selected["activities"] * travellers)

    st.subheader(f"Your {days}-day plan for {selected['place']}")
    st.caption(f"Starting point: {origin} • Month: {month} • Travellers: {travellers} • Style: {style}")
    st.info(f"Food ideas to look for: {cuisine}. These are regional suggestions, not recommendations for a specific restaurant.")

    itinerary_rows = []
    for day_no in range(1, int(days)+1):
        first = highlights[(day_no*2-2) % len(highlights)]
        second = highlights[(day_no*2-1) % len(highlights)]
        third = highlights[(day_no*2) % len(highlights)]
        with st.expander(f"Day {day_no} — {first}", expanded=(day_no == 1)):
            st.markdown(f"**8:00–9:00 AM | Breakfast**  \nTry a local breakfast or a simple meal near your stay. Keep breakfast spending within your daily food budget.")
            st.markdown(f"**9:00 AM–12:00 PM | Morning visit**  \nExplore **{first}**. Check opening hours, entry fees and travel time before leaving.")
            st.markdown(f"**12:00–2:00 PM | Lunch and rest**  \nLook for: {cuisine}. Keep some time for a relaxed lunch.")
            st.markdown(f"**2:00–5:00 PM | Afternoon visit**  \nVisit **{second}**. Use local transport and avoid trying to cover too many distant places in one day.")
            st.markdown(f"**5:00–7:00 PM | Evening option**  \nIf time and conditions allow, explore **{third}** or enjoy a nearby market/viewpoint.")
            st.markdown("**7:00 PM onward | Dinner and rest**  \nChoose a clean, well-reviewed eatery and return to your accommodation.")
            st.caption(f"Indicative group daily allowance: stay ₹{daily_stay_group:,} • food ₹{daily_food_group:,} • local travel ₹{daily_local_group:,} • activities ₹{daily_activity_group:,}.")
        itinerary_rows.append({
            "Day": day_no, "Morning": first, "Afternoon": second, "Evening option": third,
            "Breakfast": "Local breakfast near accommodation", "Lunch/Dinner idea": cuisine,
            "Group daily stay estimate (INR)": daily_stay_group,
            "Group daily food estimate (INR)": daily_food_group,
            "Group daily local travel estimate (INR)": daily_local_group,
            "Group daily activity estimate (INR)": daily_activity_group
        })

    st.subheader("Estimated trip budget")
    b1,b2,b3,b4,b5 = st.columns(5)
    b1.metric("Accommodation", f"₹{selected['stay_group']:,}")
    b2.metric("Food", f"₹{selected['food_group']:,}")
    b3.metric("Local travel", f"₹{selected['local_group']:,}")
    b4.metric("Activities", f"₹{selected['activities_group']:,}")
    b5.metric("Intercity travel", f"₹{selected['transport_group']:,}")
    st.success(f"Estimated group total: ₹{selected['total_group']:,}  |  Budget left: ₹{selected['remaining']:,}")
    st.download_button("📥 Download this day-wise itinerary (CSV)",
                       pd.DataFrame(itinerary_rows).to_csv(index=False).encode("utf-8"),
                       file_name=f"trekverse_{selected['place'].lower().replace(' ','_')}_itinerary.csv",
                       mime="text/csv")
else:
    st.info("First adjust your budget, days, travellers and filters until at least one destination appears. Then you can generate its itinerary.")

st.divider()
st.header("🗺️ V5 — Interactive India map, live weather and travel tools")

map_col, weather_col = st.columns([1.35, 1])
with map_col:
    st.subheader("Explore destinations on the map")
    map_destinations = [d for d in DESTINATIONS if d["region"] in region_filter and d["place"] in COORDS]
    if map_destinations:
        india_map = folium.Map(location=[22.5, 79.0], zoom_start=4, tiles="OpenStreetMap")
        for d in map_destinations:
            lat, lon = COORDS[d["place"]]
            popup_html = f"<b>{d['place']}</b><br>{d['state']}<br>Typical budget: ₹{d['stay']+d['food']+d['local']+d['activities']:,}/person/day"
            folium.Marker([lat,lon], tooltip=d["place"], popup=folium.Popup(popup_html, max_width=260)).add_to(india_map)
        st_folium(india_map, width=None, height=440, returned_objects=[])
        st.caption("Map pins are approximate destination/city locations. Open the map link below for navigation and verify the exact attraction pin.")
    else:
        st.info("Choose at least one region in the sidebar to display destinations.")

with weather_col:
    st.subheader("7-day weather forecast")
    weather_names = [d["place"] for d in DESTINATIONS if d["place"] in COORDS]
    weather_place = st.selectbox("Choose a destination", weather_names, key="weather_destination")
    if st.button("Get current weather and forecast"):
        with st.spinner("Fetching weather from Open-Meteo..."):
            weather_data, weather_error = fetch_weather(weather_place)
        if weather_error:
            st.warning(weather_error)
        else:
            current = weather_data.get("current", {})
            w1,w2 = st.columns(2)
            w1.metric("Temperature", f"{current.get('temperature_2m','—')} °C")
            w2.metric("Feels like", f"{current.get('apparent_temperature','—')} °C")
            w3,w4 = st.columns(2)
            w3.metric("Humidity", f"{current.get('relative_humidity_2m','—')}%")
            w4.metric("Wind", f"{current.get('wind_speed_10m','—')} km/h")
            st.write(f"**Conditions:** {weather_description(current.get('weather_code'))}")
            daily = weather_data.get("daily", {})
            forecast_rows = []
            for i, date in enumerate(daily.get("time", [])):
                forecast_rows.append({
                    "Date": date,
                    "Conditions": weather_description(daily.get("weather_code", [None]*7)[i]),
                    "Min °C": daily.get("temperature_2m_min", [None]*7)[i],
                    "Max °C": daily.get("temperature_2m_max", [None]*7)[i],
                    "Rain chance %": daily.get("precipitation_probability_max", [None]*7)[i]
                })
            if forecast_rows:
                st.dataframe(pd.DataFrame(forecast_rows), use_container_width=True, hide_index=True)
            st.caption("Forecast is from Open-Meteo. Weather changes; recheck shortly before departure.")
    st.link_button("Open destination in Google Maps", google_maps_search(weather_place))

st.divider()
st.header("🔎 Travel research and booking shortcuts")
st.write("These links help you check current details on external services. TrekVerse does not book tickets or verify live inventory.")
link_cols = st.columns(3)
with link_cols[0]:
    st.markdown("**Transport**")
    st.link_button("Search train options (IRCTC)", "https://www.irctc.co.in/")
    st.link_button("Search bus options (redBus)", "https://www.redbus.in/")
    st.link_button("Search flights (Google Flights)", "https://www.google.com/travel/flights")
with link_cols[1]:
    st.markdown("**Stays**")
    st.link_button("Search hotels (Google)", "https://www.google.com/travel/hotels")
    st.link_button("Search stays (Booking.com)", "https://www.booking.com/")
    st.link_button("Search homestays (Airbnb)", "https://www.airbnb.co.in/")
with link_cols[2]:
    st.markdown("**Destination research**")
    st.link_button("Search destination on Maps", google_maps_search(weather_place if "weather_place" in locals() else "India"))
    st.link_button("Search destination guides", "https://www.incredibleindia.gov.in/")
    st.link_button("Check India travel advisories", "https://www.mea.gov.in/")

st.divider()
st.header("🎒 Smart trip checklist")
checklist_items = [
    "Confirm return train/bus/flight tickets",
    "Confirm accommodation and cancellation policy",
    "Check forecast and local weather warnings",
    "Check attraction opening hours and entry fees",
    "Check permits and local access rules, if applicable",
    "Carry valid ID and required documents",
    "Save offline maps and emergency contacts",
    "Keep a separate emergency budget",
    "Share itinerary with a trusted person",
    "Pack medicines, chargers and suitable clothing"
]
checked = []
check_cols = st.columns(2)
for idx, item in enumerate(checklist_items):
    with check_cols[idx % 2]:
        if st.checkbox(item, key=f"trip_check_{idx}"):
            checked.append(item)
st.progress(len(checked)/len(checklist_items), text=f"{len(checked)} of {len(checklist_items)} preparation tasks completed")
if checked:
    st.download_button("Download completed checklist", pd.DataFrame({"Completed task":checked}).to_csv(index=False).encode("utf-8"),
                       file_name="trekverse_trip_checklist.csv", mime="text/csv")

st.divider()
st.header("🤖 V5 — Chat with TrekVerse")
st.write("Ask in everyday language. Try: “I have ₹5,000, want nature, and can travel for 2 days from Indore.”")

def trekverse_reply(user_text):
    q = user_text.lower()
    # Extract a budget amount such as ₹5000, 5,000 or 5k.
    budget_match = re.search(r'(?:₹|rs\.?\s*)?(\d[\d,]*)\s*(k)?', q)
    chat_budget = None
    if budget_match:
        raw = budget_match.group(1).replace(",", "")
        chat_budget = int(raw) * (1000 if budget_match.group(2) else 1)
        if chat_budget < 500:
            chat_budget = None

    day_match = re.search(r'(\d{1,2})\s*(?:days?|nights?)', q)
    chat_days = int(day_match.group(1)) if day_match else int(days)
    chat_days = max(1, min(chat_days, 21))

    # Infer interests from the words the user uses.
    interest_map = {
        "Nature": ["nature", "mountain", "hill", "waterfall", "lake", "beach", "scenery", "greenery"],
        "Adventure": ["adventure", "trek", "trekking", "rafting", "camping", "hiking"],
        "Snow": ["snow", "snowfall", "winter"],
        "Food": ["food", "eat", "cuisine", "street food", "restaurant"],
        "Shopping": ["shopping", "market", "buy", "bazaar"],
        "Historical": ["history", "historical", "fort", "palace", "monument", "heritage"],
        "Spiritual": ["temple", "spiritual", "pilgrimage", "religious"],
        "Culture": ["culture", "cultural", "festival", "tradition"],
        "Architecture": ["architecture", "building"],
        "Wildlife": ["wildlife", "safari", "animals", "tiger"]
    }
    wanted = [tag for tag, words in interest_map.items() if any(w in q for w in words)]

    # Destination-specific question: give details from the bundled dataset.
    mentioned = next((d for d in DESTINATIONS if d["place"].lower() in q), None)
    if mentioned:
        daily = mentioned["stay"] + mentioned["food"] + mentioned["local"] + mentioned["activities"]
        return (
            f"**{mentioned['place']}, {mentioned['state']} ({mentioned['region']} India)**\n\n"
            f"{', '.join(mentioned['highlights'])} are listed highlights. "
            f"Interests: {', '.join(mentioned['tags'])}. General season guide: {mentioned['months']}.\n\n"
            f"Illustrative destination spending is about **₹{daily:,} per person per day** "
            f"for stay, food, local travel and activities, before intercity transport. "
            "This is a planning estimate, not a live quote. Check current prices, access, permits and weather."
        )

    # Find matching destinations from the local database using chat constraints.
    selected_budget = chat_budget if chat_budget else int(budget)
    selected_travellers = int(travellers)
    fare_pp = int(transport_pp)
    candidates = []
    for d in DESTINATIONS:
        if d["region"] not in region_filter:
            continue
        if wanted and not set(wanted).intersection(d["tags"]):
            continue
        comfort_multiplier = 1.35 if style == "Comfortable" else 1.0
        stay_cost = round(d["stay"] * chat_days * comfort_multiplier)
        food_cost = round(d["food"] * chat_days * (1.15 if style == "Comfortable" else 1.0))
        local_cost = round(d["local"] * chat_days)
        activity_cost = round(d["activities"] * chat_days)
        destination_cost = (stay_cost + food_cost + local_cost + activity_cost) * selected_travellers
        travel_cost = fare_pp * selected_travellers
        total = destination_cost + travel_cost
        if total <= selected_budget:
            score = len(set(wanted).intersection(d["tags"])) * 4
            candidates.append((score, total, d, stay_cost, food_cost, local_cost, activity_cost))
    candidates.sort(key=lambda item: (item[0], -item[1]), reverse=True)

    if candidates:
        lines = [
            f"Based on **₹{selected_budget:,} total**, **{selected_travellers} traveller(s)** and **{chat_days} day(s)**, here are options from the TrekVerse destination database:",
            ""
        ]
        for score, total, d, stay_cost, food_cost, local_cost, activity_cost in candidates[:5]:
            lines.append(
                f"- **{d['place']}, {d['state']}** — estimated group total **₹{total:,}** "
                f"(stay ₹{stay_cost*selected_travellers:,}, food ₹{food_cost*selected_travellers:,}, "
                f"local travel ₹{local_cost*selected_travellers:,}, activities ₹{activity_cost*selected_travellers:,}, "
                f"intercity fare ₹{fare_pp*selected_travellers:,}). "
                f"Highlights: {', '.join(d['highlights'][:2])}."
            )
        if fare_pp == 0:
            lines += ["", "**Transport note:** You have not entered an intercity return fare, so these totals exclude travel from your starting city to the destination. Add a checked fare in the sidebar for a more complete estimate."]
        lines += ["", "These are illustrative estimates, not live hotel, train or bus prices. Compare actual fares and accommodation before booking."]
        return "\n".join(lines)

    if wanted:
        wanted_text = ", ".join(wanted)
    else:
        wanted_text = "your selected interests"
    return (
        f"I couldn't find a destination in the current database that fits **₹{selected_budget:,}** "
        f"for **{chat_days} day(s)** and {wanted_text}. Try increasing the budget, reducing the trip length, "
        "changing the region filter, or entering a lower checked intercity fare. "
        "If you haven't entered a transport fare, remember that recommendations exclude the journey to the destination."
    )

if "trekverse_chat_history" not in st.session_state:
    st.session_state.trekverse_chat_history = [
        {"role": "assistant", "content": "Hello! I'm TrekVerse. Tell me your budget, starting city, number of days and the kind of trip you like. I can compare destinations using the built-in India travel database."}
    ]

for message in st.session_state.trekverse_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask TrekVerse about a trip, budget or destination...")
if user_prompt:
    st.session_state.trekverse_chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    answer = trekverse_reply(user_prompt)
    st.session_state.trekverse_chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

if st.button("Clear chat history"):
    st.session_state.trekverse_chat_history = []
    st.rerun()

with st.expander("How estimates work and what is not included"):
    st.write("Per-person destination estimate = (daily accommodation + daily food + daily local travel + daily activities) × number of days. Group costs multiply by travellers and add the round-trip transport fare you entered per person.")
    st.warning("These are broad illustrative estimates, not verified live prices. The itinerary rotates the destination highlights to create a sample schedule; it does not know live opening hours, route distances, traffic, restaurant availability or weather. Check current prices, permits, opening days and local advisories before booking.")
st.caption("TrekVerse India Edition V3 • Python + Streamlit + Pandas • Free starter project")
