import streamlit as st
import pandas as pd
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
st.title("🧭 TrekVerse — Explore India on Your Budget")
st.write("Compare destinations across India, estimate trip costs and build a simple day-wise plan.")
st.caption("Free starter version • No paid AI API • 60+ destinations • No live fares or hotel quotes")
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
    st.warning("No listed destination fits the current inputs. Try more budget, fewer days, fewer travellers, or set a lower checked transport estimate.")
else:
    for p in matches[:12]:
        with st.expander(f"📍 {p['place']}, {p['state']} — estimated group total ₹{p['total_group']:,}"):
            st.write(f"**Region:** {p['region']}  |  **Best season (general guide):** {p['months']}")
            st.write(f"**Why visit:** {', '.join(p['highlights'])}")
            st.write(f"**Interests:** {', '.join(p['tags'])}")
            x1,x2,x3,x4,x5 = st.columns(5)
            x1.metric("Stay",f"₹{p['stay_group']:,}")
            x2.metric("Food",f"₹{p['food_group']:,}")
            x3.metric("Local travel",f"₹{p['local_group']:,}")
            x4.metric("Activities",f"₹{p['activities_group']:,}")
            x5.metric("Intercity travel",f"₹{p['transport_group']:,}")
            st.success(f"Estimated remaining budget: ₹{p['remaining']:,}")
            st.markdown("**Simple day-wise idea**")
            highlights = p["highlights"]
            for day in range(1, int(days)+1):
                first = highlights[(day-1) % len(highlights)]
                second = highlights[day % len(highlights)]
                st.write(f"Day {day}: Explore {first}; then visit {second}. Keep time for meals, rest and local transport.")
            st.caption("Check opening days, permits, weather, road conditions and current prices before booking.")

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
st.subheader("Ask TrekVerse")
question = st.text_input("Ask a simple travel question", placeholder="Example: Which low-cost places are good for nature?")
if question:
    q = question.lower()
    if "snow" in q:
        names = [d["place"] for d in DESTINATIONS if "Snow" in d["tags"]]
        st.info("Snow-oriented options in this database: " + ", ".join(names) + ". Snow is seasonal and never guaranteed.")
    elif any(w in q for w in ["food","eat","cuisine"]):
        names = [d["place"] for d in DESTINATIONS if "Food" in d["tags"]]
        st.info("Food-oriented options include: " + ", ".join(names[:18]) + ".")
    elif any(w in q for w in ["beach","sea"]):
        names = [d["place"] for d in DESTINATIONS if "Nature" in d["tags"] and d["region"] in ["West","South","Islands"]]
        st.info("Coastal/island options to explore include: " + ", ".join(names[:18]) + ".")
    else:
        st.info("I can answer simple questions using the destination database. This is a rule-based assistant, not a generative AI chatbot yet.")

with st.expander("How estimates work and what is not included"):
    st.write("Per-person destination estimate = (daily accommodation + daily food + daily local travel + daily activities) × number of days. The group total multiplies this by travellers and adds the round-trip transport amount you entered per person.")
    st.warning("These are broad illustrative estimates, not verified live prices. Actual costs vary by date, city area, season, group size, accommodation type and transport mode. Some places require permits, guides, ferries or special transport that may not be included. For remote destinations, check local advisories and access conditions.")
st.caption("TrekVerse India Edition • Python + Streamlit + Pandas • Free starter project")
