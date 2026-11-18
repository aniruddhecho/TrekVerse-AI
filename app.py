import streamlit as st
import pandas as pd

st.set_page_config(page_title="TrekVerse | Travel on a Budget", page_icon="🧭", layout="wide")

# Starter dataset: rough planning estimates for one person travelling from Indore.
# These are NOT live fares or hotel quotes. Update them with current prices before booking.
PLACES = [
    {"place":"Ujjain","state":"Madhya Pradesh","days":1,"travel":350,"stay":0,"food":450,"local":250,"tags":["Historical","Food"],"best":"October to March","why":"Mahakaleshwar Jyotirlinga, temples and a simple day trip."},
    {"place":"Mandu","state":"Madhya Pradesh","days":2,"travel":900,"stay":700,"food":700,"local":450,"tags":["Nature","Historical","Adventure"],"best":"July to February","why":"Fort ruins, viewpoints, lakes and monsoon scenery."},
    {"place":"Omkareshwar","state":"Madhya Pradesh","days":2,"travel":900,"stay":700,"food":650,"local":350,"tags":["Nature","Historical"],"best":"October to March","why":"Narmada river, island temples and peaceful walks."},
    {"place":"Maheshwar","state":"Madhya Pradesh","days":2,"travel":900,"stay":800,"food":700,"local":400,"tags":["Nature","Historical","Shopping"],"best":"October to March","why":"Ahilya Fort, ghats, Narmada views and handloom sarees."},
    {"place":"Bhopal","state":"Madhya Pradesh","days":2,"travel":1100,"stay":900,"food":800,"local":500,"tags":["Food","Historical","Nature"],"best":"October to March","why":"Lakes, museums, old-city food and nearby heritage sites."},
    {"place":"Pachmarhi","state":"Madhya Pradesh","days":3,"travel":2200,"stay":1800,"food":1100,"local":1000,"tags":["Nature","Adventure"],"best":"October to June","why":"Hill-station views, waterfalls and forest trails."},
    {"place":"Jaipur","state":"Rajasthan","days":3,"travel":2600,"stay":1800,"food":1200,"local":900,"tags":["Historical","Food","Shopping"],"best":"October to March","why":"Forts, palaces, markets and Rajasthani food."},
    {"place":"Ahmedabad","state":"Gujarat","days":2,"travel":2200,"stay":1200,"food":900,"local":700,"tags":["Historical","Food","Shopping"],"best":"November to February","why":"Heritage streets, museums, food and stepwells nearby."},
    {"place":"Nashik","state":"Maharashtra","days":2,"travel":2200,"stay":1300,"food":900,"local":700,"tags":["Nature","Historical","Food"],"best":"October to March","why":"Temples, vineyards, hills and scenic surroundings."},
    {"place":"Rishikesh","state":"Uttarakhand","days":4,"travel":4200,"stay":2400,"food":1500,"local":1200,"tags":["Adventure","Nature"],"best":"September to April","why":"Ganga riverfront, yoga, hiking and adventure activities."},
    {"place":"Manali","state":"Himachal Pradesh","days":5,"travel":6500,"stay":3500,"food":2000,"local":1800,"tags":["Snow","Adventure","Nature"],"best":"March to June; December to February for snow","why":"Mountain scenery, trekking and seasonal snow."},
    {"place":"Goa","state":"Goa","days":4,"travel":6000,"stay":3000,"food":1800,"local":1500,"tags":["Nature","Food","Adventure"],"best":"November to February","why":"Beaches, coastal food, markets and water activities."},
]

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
INTERESTS = ["Adventure","Nature","Snow","Food","Shopping","Historical"]

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#071b2b 0%,#102f3d 55%,#173b42 100%); color:#f4f7f8;}
h1,h2,h3,p,label {color:#f4f7f8 !important;}
.block-container {max-width:1100px; padding-top:2rem;}
.hero {padding:24px 28px; border:1px solid #42616a; border-radius:18px; background:rgba(255,255,255,.06); margin-bottom:20px;}
.card {padding:18px; border:1px solid #47636a; border-radius:14px; background:rgba(255,255,255,.07); margin:10px 0;}
.small {color:#c2d2d5; font-size: .9rem;}
div.stButton > button {background:#12a9ce;color:white;border:0;border-radius:9px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero">', unsafe_allow_html=True)
st.title("🧭 TrekVerse AI Travel Assistant")
st.write("Find trips that fit your money, days and interests — without paid APIs or API keys.")
st.caption("Beginner-friendly free starter project • Estimates are illustrative, not live booking prices.")
st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Your trip details")
    origin = st.text_input("Starting city", "Indore")
    budget = st.number_input("Total budget (₹)", min_value=500, max_value=500000, value=5000, step=500)
    travellers = st.number_input("Number of travellers", min_value=1, max_value=20, value=1)
    days = st.slider("Number of days", 1, 14, 2)
    month = st.selectbox("Travel month", MONTHS, index=10)
    interests = st.multiselect("What do you enjoy?", INTERESTS, default=["Nature","Historical"])
    comfort = st.selectbox("Travel style", ["Budget","Comfortable"], index=0)
    search = st.button("Find my trips", use_container_width=True)

st.subheader("Your budget")
c1,c2,c3 = st.columns(3)
c1.metric("Total budget", f"₹{budget:,.0f}")
c2.metric("Travellers", int(travellers))
c3.metric("Budget per person", f"₹{budget/travellers:,.0f}")

if search or "results" not in st.session_state:
    st.session_state.results = True

# Estimates in PLACES are per person, for the listed typical duration, starting from Indore.
# Scale lodging/food/local costs by requested days; transport is a rough round-trip estimate.
results = []
per_person_budget = budget / travellers
for p in PLACES:
    ratio = days / p["days"]
    stay = p["stay"] * ratio
    food = p["food"] * ratio
    local = p["local"] * ratio
    transport = p["travel"]
    if comfort == "Comfortable":
        stay *= 1.65
        food *= 1.25
    estimated_person = transport + stay + food + local
    estimated_group = estimated_person * travellers
    if days < 1 or estimated_group > budget:
        continue
    interest_matches = len(set(interests).intersection(p["tags"]))
    # Prefer places whose usual trip length is close to the selected duration.
    day_fit = max(0, 1 - abs(days-p["days"])/max(days,p["days"]))
    score = (interest_matches * 3) + (day_fit * 2) + (2 if estimated_group <= budget*0.8 else 0)
    results.append({**p, "estimate_person":round(estimated_person), "estimate_group":round(estimated_group),
                    "left":round(budget-estimated_group), "score":score})

results.sort(key=lambda x:(x["score"], -x["estimate_group"]), reverse=True)

st.subheader("Recommended destinations")
st.caption(f"Planning from **{origin}**. Important: the built-in transport estimates are currently based on an example journey from Indore. If your starting city is different, treat transport costs as placeholders.")
if not results:
    st.warning("No destination in the starter list fits this budget and duration. Try increasing the budget or reducing the number of days.")
else:
    shown = results[:6]
    for p in shown:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            left,right = st.columns([3,1])
            with left:
                st.subheader(f"📍 {p['place']}, {p['state']}")
                st.write(p["why"])
                st.caption(f"Interests: {', '.join(p['tags'])} • Usually best: {p['best']}")
                st.caption(f"Suggested duration in starter data: {p['days']} day(s)")
            with right:
                st.metric("Estimated total", f"₹{p['estimate_group']:,}")
                st.metric("Budget remaining", f"₹{p['left']:,}")
            st.markdown('</div>', unsafe_allow_html=True)

    df = pd.DataFrame([{
        "Destination":p["place"], "Estimated total for group (₹)":p["estimate_group"],
        "Estimated per person (₹)":p["estimate_person"], "Budget left (₹)":p["left"],
        "Suggested days":p["days"], "Best season":p["best"]
    } for p in shown])
    st.download_button("⬇️ Download recommendations (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name="trekverse_recommendations.csv", mime="text/csv")

st.divider()
st.subheader("Ask TrekVerse")
question = st.text_input("Ask a travel question", placeholder="Example: Suggest a cheap nature trip for 2 days.")
if question:
    q = question.lower()
    if any(word in q for word in ["cheap","budget","5000","low cost"]):
        st.info("Tip: sort your budget in the sidebar and choose Budget travel style. The recommendations above are ranked by your interests and estimated cost.")
    elif "snow" in q:
        snow = [p["place"] for p in PLACES if "Snow" in p["tags"]]
        st.info("Snow-related starter destination: " + ", ".join(snow) + ". Snow depends heavily on season and weather.")
    elif any(word in q for word in ["food","eat","cuisine"]):
        food = [p["place"] for p in PLACES if "Food" in p["tags"]]
        st.info("Food-focused options in this starter list: " + ", ".join(food) + ".")
    else:
        st.info("I can currently answer simple questions using the built-in destination list. This starter version uses recommendation rules, not a paid generative-AI service.")

with st.expander("How are the estimates calculated?"):
    st.write("Estimated group cost = (rough round-trip transport + accommodation + food + local travel) per person × number of travellers. Accommodation, food and local travel are scaled to your selected number of days. Comfortable mode increases stay and food estimates.")
    st.warning("These are sample planning estimates, not verified current prices. They do not guarantee availability and may exclude entry tickets, seasonal surcharges, permits, emergencies or price changes. Check current train/bus fares and accommodation before paying.")

st.caption("Weather data is not connected in this starter version. Future upgrade: add Open-Meteo weather forecasts (free for non-commercial use, no API key; attribution required).")
st.caption("Made with Python + Streamlit. Streamlit is open source.")
