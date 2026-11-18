import streamlit as st
import pandas as pd
import requests
import re, io, math
from urllib.parse import quote_plus
import folium
from streamlit_folium import st_folium
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="TrekVerse V6 | India Travel OS", page_icon="🧭", layout="wide")
DESTINATIONS = [{'place': 'Amritsar', 'state': 'Punjab', 'region': 'North', 'stay': 700, 'food': 500, 'local': 250, 'activities': 200, 'tags': ['Historical', 'Food', 'Culture'], 'months': 'October–March', 'highlights': ['Golden Temple', 'Jallianwala Bagh', 'Wagah border ceremony']}, {'place': 'Chandigarh', 'state': 'Chandigarh', 'region': 'North', 'stay': 900, 'food': 600, 'local': 350, 'activities': 250, 'tags': ['Nature', 'Architecture', 'Food'], 'months': 'October–March', 'highlights': ['Rock Garden', 'Sukhna Lake', 'Capitol Complex']}, {'place': 'Shimla', 'state': 'Himachal Pradesh', 'region': 'North', 'stay': 1000, 'food': 650, 'local': 450, 'activities': 300, 'tags': ['Nature', 'Adventure', 'Snow'], 'months': 'March–June; December–February for snow', 'highlights': ['The Ridge', 'Mall Road', 'Kufri']}, {'place': 'Manali', 'state': 'Himachal Pradesh', 'region': 'North', 'stay': 1100, 'food': 650, 'local': 500, 'activities': 450, 'tags': ['Nature', 'Adventure', 'Snow'], 'months': 'March–June; December–February for snow', 'highlights': ['Old Manali', 'Hadimba Temple', 'Solang Valley']}, {'place': 'Dharamshala and McLeod Ganj', 'state': 'Himachal Pradesh', 'region': 'North', 'stay': 900, 'food': 600, 'local': 350, 'activities': 250, 'tags': ['Nature', 'Adventure', 'Culture'], 'months': 'March–June; September–November', 'highlights': ['Bhagsu Waterfall', 'Dalai Lama Temple', 'Triund trail']}, {'place': 'Kasol', 'state': 'Himachal Pradesh', 'region': 'North', 'stay': 800, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Nature', 'Adventure'], 'months': 'March–June; September–November', 'highlights': ['Parvati River', 'Chalal walk', 'Tosh village']}, {'place': 'Rishikesh', 'state': 'Uttarakhand', 'region': 'North', 'stay': 700, 'food': 500, 'local': 300, 'activities': 500, 'tags': ['Nature', 'Adventure', 'Spiritual'], 'months': 'September–April', 'highlights': ['Ganga aarti', 'Ram Jhula', 'River rafting (seasonal)']}, {'place': 'Haridwar', 'state': 'Uttarakhand', 'region': 'North', 'stay': 650, 'food': 450, 'local': 250, 'activities': 150, 'tags': ['Spiritual', 'Historical', 'Culture'], 'months': 'October–March', 'highlights': ['Har Ki Pauri', 'Mansa Devi Temple', 'Ganga aarti']}, {'place': 'Nainital', 'state': 'Uttarakhand', 'region': 'North', 'stay': 900, 'food': 550, 'local': 350, 'activities': 300, 'tags': ['Nature', 'Adventure'], 'months': 'March–June; September–November', 'highlights': ['Naini Lake', 'Snow View Point', 'Mall Road']}, {'place': 'Jaipur', 'state': 'Rajasthan', 'region': 'North', 'stay': 800, 'food': 550, 'local': 300, 'activities': 350, 'tags': ['Historical', 'Food', 'Shopping', 'Architecture'], 'months': 'October–March', 'highlights': ['Amber Fort', 'Hawa Mahal', 'City Palace']}, {'place': 'Udaipur', 'state': 'Rajasthan', 'region': 'North', 'stay': 1000, 'food': 650, 'local': 350, 'activities': 350, 'tags': ['Historical', 'Nature', 'Food', 'Culture'], 'months': 'October–March', 'highlights': ['Lake Pichola', 'City Palace', 'Bagore Ki Haveli']}, {'place': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North', 'stay': 800, 'food': 550, 'local': 300, 'activities': 300, 'tags': ['Historical', 'Food', 'Shopping'], 'months': 'October–March', 'highlights': ['Mehrangarh Fort', 'Blue City lanes', 'Jaswant Thada']}, {'place': 'Jaisalmer', 'state': 'Rajasthan', 'region': 'North', 'stay': 900, 'food': 600, 'local': 350, 'activities': 600, 'tags': ['Historical', 'Adventure', 'Culture'], 'months': 'October–March', 'highlights': ['Jaisalmer Fort', 'Sam Sand Dunes', 'Patwon Ki Haveli']}, {'place': 'Pushkar', 'state': 'Rajasthan', 'region': 'North', 'stay': 700, 'food': 500, 'local': 250, 'activities': 200, 'tags': ['Spiritual', 'Historical', 'Shopping'], 'months': 'October–March', 'highlights': ['Pushkar Lake', 'Brahma Temple', 'Local bazaar']}, {'place': 'Ujjain', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 650, 'food': 450, 'local': 250, 'activities': 200, 'tags': ['Spiritual', 'Historical', 'Food'], 'months': 'October–March', 'highlights': ['Mahakaleshwar Temple', 'Ram Ghat', 'Kal Bhairav Temple']}, {'place': 'Mandu', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 700, 'food': 450, 'local': 300, 'activities': 250, 'tags': ['Nature', 'Historical', 'Architecture'], 'months': 'July–February', 'highlights': ['Jahaz Mahal', 'Hindola Mahal', 'Rani Roopmati Pavilion']}, {'place': 'Maheshwar', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 750, 'food': 500, 'local': 250, 'activities': 200, 'tags': ['Nature', 'Historical', 'Shopping', 'Culture'], 'months': 'October–March', 'highlights': ['Ahilya Fort', 'Narmada ghats', 'Maheshwari handloom']}, {'place': 'Bhopal', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 750, 'food': 500, 'local': 300, 'activities': 250, 'tags': ['Nature', 'Historical', 'Food'], 'months': 'October–March', 'highlights': ['Upper Lake', 'Tribal Museum', 'Sanchi day trip']}, {'place': 'Pachmarhi', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 1000, 'food': 550, 'local': 550, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'October–June', 'highlights': ['Bee Falls', 'Dhoopgarh', 'Pandav Caves']}, {'place': 'Khajuraho', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 800, 'food': 500, 'local': 250, 'activities': 350, 'tags': ['Historical', 'Architecture', 'Culture'], 'months': 'October–March', 'highlights': ['Western Group of Temples', 'Eastern temples', 'Raneh Falls']}, {'place': 'Orchha', 'state': 'Madhya Pradesh', 'region': 'Central', 'stay': 650, 'food': 450, 'local': 200, 'activities': 200, 'tags': ['Historical', 'Nature', 'Architecture'], 'months': 'October–March', 'highlights': ['Orchha Fort complex', 'Chaturbhuj Temple', 'Betwa River']}, {'place': 'Varanasi', 'state': 'Uttar Pradesh', 'region': 'Central', 'stay': 750, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Spiritual', 'Historical', 'Food', 'Culture'], 'months': 'October–March', 'highlights': ['Dashashwamedh Ghat', 'Kashi Vishwanath Temple', 'Sarnath']}, {'place': 'Agra', 'state': 'Uttar Pradesh', 'region': 'Central', 'stay': 800, 'food': 550, 'local': 300, 'activities': 450, 'tags': ['Historical', 'Architecture', 'Food'], 'months': 'October–March', 'highlights': ['Taj Mahal', 'Agra Fort', 'Fatehpur Sikri']}, {'place': 'Lucknow', 'state': 'Uttar Pradesh', 'region': 'Central', 'stay': 800, 'food': 650, 'local': 300, 'activities': 250, 'tags': ['Historical', 'Food', 'Architecture'], 'months': 'October–March', 'highlights': ['Bara Imambara', 'Rumi Darwaza', 'Awadhi food trail']}, {'place': 'Mumbai', 'state': 'Maharashtra', 'region': 'West', 'stay': 1300, 'food': 750, 'local': 450, 'activities': 350, 'tags': ['Food', 'Historical', 'Shopping', 'Nature'], 'months': 'November–February', 'highlights': ['Gateway of India', 'Marine Drive', 'Elephanta Caves']}, {'place': 'Pune', 'state': 'Maharashtra', 'region': 'West', 'stay': 900, 'food': 650, 'local': 350, 'activities': 250, 'tags': ['Historical', 'Food', 'Nature'], 'months': 'October–February', 'highlights': ['Shaniwar Wada', 'Aga Khan Palace', 'Sinhagad Fort']}, {'place': 'Nashik', 'state': 'Maharashtra', 'region': 'West', 'stay': 850, 'food': 550, 'local': 350, 'activities': 250, 'tags': ['Nature', 'Spiritual', 'Food'], 'months': 'October–March', 'highlights': ['Trimbakeshwar', 'Pandavleni Caves', 'Godavari ghats']}, {'place': 'Mahabaleshwar', 'state': 'Maharashtra', 'region': 'West', 'stay': 1100, 'food': 600, 'local': 450, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'October–June', 'highlights': ['Venna Lake', "Arthur's Seat", 'Mapro Garden']}, {'place': 'Goa', 'state': 'Goa', 'region': 'West', 'stay': 1200, 'food': 700, 'local': 500, 'activities': 450, 'tags': ['Nature', 'Food', 'Adventure', 'Shopping'], 'months': 'November–February', 'highlights': ['Beaches', 'Old Goa churches', 'Local markets']}, {'place': 'Ahmedabad', 'state': 'Gujarat', 'region': 'West', 'stay': 800, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Historical', 'Food', 'Shopping', 'Architecture'], 'months': 'November–February', 'highlights': ['Sabarmati Ashram', 'Adalaj Stepwell', 'Old city heritage walk']}, {'place': 'Rann of Kutch', 'state': 'Gujarat', 'region': 'West', 'stay': 1400, 'food': 650, 'local': 650, 'activities': 500, 'tags': ['Nature', 'Culture', 'Photography'], 'months': 'November–February', 'highlights': ['White Rann', 'Kala Dungar', 'Craft villages']}, {'place': 'Diu', 'state': 'Dadra and Nagar Haveli and Daman and Diu', 'region': 'West', 'stay': 900, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Nature', 'Historical', 'Food'], 'months': 'October–March', 'highlights': ['Diu Fort', 'Nagoa Beach', 'Naida Caves']}, {'place': 'Hyderabad', 'state': 'Telangana', 'region': 'South', 'stay': 900, 'food': 650, 'local': 350, 'activities': 350, 'tags': ['Historical', 'Food', 'Shopping', 'Architecture'], 'months': 'October–February', 'highlights': ['Charminar', 'Golconda Fort', 'Hussain Sagar']}, {'place': 'Hampi', 'state': 'Karnataka', 'region': 'South', 'stay': 800, 'food': 550, 'local': 350, 'activities': 300, 'tags': ['Historical', 'Nature', 'Adventure', 'Architecture'], 'months': 'October–February', 'highlights': ['Virupaksha Temple', 'Vittala Temple', 'Hampi bazaar']}, {'place': 'Bengaluru', 'state': 'Karnataka', 'region': 'South', 'stay': 1100, 'food': 750, 'local': 400, 'activities': 300, 'tags': ['Food', 'Nature', 'Shopping'], 'months': 'October–February', 'highlights': ['Lalbagh', 'Cubbon Park', 'Bengaluru food streets']}, {'place': 'Mysuru', 'state': 'Karnataka', 'region': 'South', 'stay': 850, 'food': 600, 'local': 300, 'activities': 300, 'tags': ['Historical', 'Culture', 'Food', 'Architecture'], 'months': 'October–March', 'highlights': ['Mysore Palace', 'Chamundi Hills', 'Devaraja Market']}, {'place': 'Coorg', 'state': 'Karnataka', 'region': 'South', 'stay': 1100, 'food': 650, 'local': 500, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'October–March', 'highlights': ['Abbey Falls', "Raja's Seat", 'Coffee estates']}, {'place': 'Gokarna', 'state': 'Karnataka', 'region': 'South', 'stay': 900, 'food': 550, 'local': 350, 'activities': 250, 'tags': ['Nature', 'Adventure'], 'months': 'October–March', 'highlights': ['Om Beach', 'Kudle Beach', 'Coastal trail']}, {'place': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South', 'stay': 1000, 'food': 650, 'local': 400, 'activities': 300, 'tags': ['Food', 'Historical', 'Culture'], 'months': 'November–February', 'highlights': ['Marina Beach', 'Kapaleeshwarar Temple', 'Fort St. George']}, {'place': 'Ooty', 'state': 'Tamil Nadu', 'region': 'South', 'stay': 1100, 'food': 600, 'local': 450, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'October–June', 'highlights': ['Botanical Gardens', 'Ooty Lake', 'Nilgiri Mountain Railway']}, {'place': 'Kodaikanal', 'state': 'Tamil Nadu', 'region': 'South', 'stay': 1000, 'food': 600, 'local': 450, 'activities': 300, 'tags': ['Nature', 'Adventure'], 'months': 'October–June', 'highlights': ['Kodaikanal Lake', "Coaker's Walk", 'Pillar Rocks']}, {'place': 'Madurai', 'state': 'Tamil Nadu', 'region': 'South', 'stay': 750, 'food': 550, 'local': 250, 'activities': 250, 'tags': ['Spiritual', 'Historical', 'Food', 'Architecture'], 'months': 'October–March', 'highlights': ['Meenakshi Amman Temple', 'Thirumalai Nayakkar Palace', 'Local food streets']}, {'place': 'Rameswaram', 'state': 'Tamil Nadu', 'region': 'South', 'stay': 800, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Spiritual', 'Nature', 'Historical'], 'months': 'October–April', 'highlights': ['Ramanathaswamy Temple', 'Pamban Bridge', 'Dhanushkodi']}, {'place': 'Kochi', 'state': 'Kerala', 'region': 'South', 'stay': 1000, 'food': 650, 'local': 350, 'activities': 300, 'tags': ['Historical', 'Food', 'Culture', 'Nature'], 'months': 'October–March', 'highlights': ['Fort Kochi', 'Chinese fishing nets', 'Mattancherry Palace']}, {'place': 'Munnar', 'state': 'Kerala', 'region': 'South', 'stay': 1200, 'food': 650, 'local': 500, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'September–March', 'highlights': ['Tea gardens', 'Eravikulam National Park', 'Mattupetty Dam']}, {'place': 'Alappuzha', 'state': 'Kerala', 'region': 'South', 'stay': 1000, 'food': 650, 'local': 350, 'activities': 450, 'tags': ['Nature', 'Food'], 'months': 'November–February', 'highlights': ['Backwaters', 'Alappuzha Beach', 'Village canoe trip']}, {'place': 'Varkala', 'state': 'Kerala', 'region': 'South', 'stay': 1000, 'food': 650, 'local': 350, 'activities': 300, 'tags': ['Nature', 'Adventure', 'Food'], 'months': 'October–March', 'highlights': ['Varkala cliff', 'Papanasam Beach', 'Janardhana Swamy Temple']}, {'place': 'Puducherry', 'state': 'Puducherry', 'region': 'South', 'stay': 1000, 'food': 700, 'local': 350, 'activities': 300, 'tags': ['Nature', 'Food', 'Historical', 'Culture'], 'months': 'October–March', 'highlights': ['White Town', 'Promenade Beach', 'Auroville']}, {'place': 'Kolkata', 'state': 'West Bengal', 'region': 'East', 'stay': 850, 'food': 600, 'local': 300, 'activities': 300, 'tags': ['Historical', 'Food', 'Culture', 'Architecture'], 'months': 'October–February', 'highlights': ['Victoria Memorial', 'Howrah Bridge', 'College Street']}, {'place': 'Darjeeling', 'state': 'West Bengal', 'region': 'East', 'stay': 1100, 'food': 650, 'local': 450, 'activities': 350, 'tags': ['Nature', 'Adventure'], 'months': 'March–May; October–November', 'highlights': ['Tiger Hill', 'Tea gardens', 'Darjeeling Himalayan Railway']}, {'place': 'Gangtok', 'state': 'Sikkim', 'region': 'East', 'stay': 1100, 'food': 650, 'local': 450, 'activities': 350, 'tags': ['Nature', 'Adventure', 'Culture'], 'months': 'March–June; September–November', 'highlights': ['MG Marg', 'Tsomgo Lake', 'Rumtek Monastery']}, {'place': 'Shillong', 'state': 'Meghalaya', 'region': 'East', 'stay': 1000, 'food': 600, 'local': 450, 'activities': 350, 'tags': ['Nature', 'Adventure', 'Food'], 'months': 'October–April', 'highlights': ['Umiam Lake', 'Elephant Falls', 'Laitlum Canyon']}, {'place': 'Cherrapunji (Sohra)', 'state': 'Meghalaya', 'region': 'East', 'stay': 1000, 'food': 600, 'local': 550, 'activities': 400, 'tags': ['Nature', 'Adventure'], 'months': 'October–May', 'highlights': ['Nohkalikai Falls', 'Mawsmai Cave', 'Living root bridges']}, {'place': 'Kaziranga', 'state': 'Assam', 'region': 'East', 'stay': 1200, 'food': 650, 'local': 600, 'activities': 900, 'tags': ['Nature', 'Adventure', 'Wildlife'], 'months': 'November–April', 'highlights': ['Kaziranga safari', 'Orchid park', 'Brahmaputra river']}, {'place': 'Guwahati', 'state': 'Assam', 'region': 'East', 'stay': 850, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Spiritual', 'Nature', 'Food'], 'months': 'October–April', 'highlights': ['Kamakhya Temple', 'Brahmaputra riverfront', 'Umananda Island']}, {'place': 'Tawang', 'state': 'Arunachal Pradesh', 'region': 'East', 'stay': 1300, 'food': 650, 'local': 700, 'activities': 350, 'tags': ['Nature', 'Adventure', 'Snow', 'Culture'], 'months': 'April–October; winter conditions can be severe', 'highlights': ['Tawang Monastery', 'Sela Pass', 'Madhuri Lake']}, {'place': 'Puri', 'state': 'Odisha', 'region': 'East', 'stay': 800, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Spiritual', 'Nature', 'Food'], 'months': 'October–February', 'highlights': ['Jagannath Temple', 'Puri Beach', 'Konark Sun Temple']}, {'place': 'Bhubaneswar', 'state': 'Odisha', 'region': 'East', 'stay': 800, 'food': 550, 'local': 300, 'activities': 250, 'tags': ['Historical', 'Architecture', 'Food'], 'months': 'October–February', 'highlights': ['Lingaraj Temple', 'Udayagiri and Khandagiri Caves', 'Dhauli']}, {'place': 'Ranchi', 'state': 'Jharkhand', 'region': 'East', 'stay': 750, 'food': 500, 'local': 350, 'activities': 250, 'tags': ['Nature', 'Adventure'], 'months': 'October–March', 'highlights': ['Hundru Falls', 'Dassam Falls', 'Rock Garden']}, {'place': 'Raipur', 'state': 'Chhattisgarh', 'region': 'Central', 'stay': 800, 'food': 550, 'local': 350, 'activities': 250, 'tags': ['Food', 'Nature', 'Culture'], 'months': 'October–March', 'highlights': ['Nandan Van', 'Purkhouti Muktangan', 'Sirpur day trip']}, {'place': 'Visakhapatnam', 'state': 'Andhra Pradesh', 'region': 'South', 'stay': 900, 'food': 600, 'local': 350, 'activities': 300, 'tags': ['Nature', 'Food', 'Adventure'], 'months': 'October–March', 'highlights': ['RK Beach', 'Kailasagiri', 'Submarine Museum']}, {'place': 'Araku Valley', 'state': 'Andhra Pradesh', 'region': 'South', 'stay': 900, 'food': 550, 'local': 500, 'activities': 300, 'tags': ['Nature', 'Adventure'], 'months': 'October–March', 'highlights': ['Borra Caves', 'Coffee plantations', 'Araku viewpoints']}, {'place': 'Port Blair (Sri Vijaya Puram)', 'state': 'Andaman and Nicobar Islands', 'region': 'Islands', 'stay': 1500, 'food': 800, 'local': 600, 'activities': 900, 'tags': ['Nature', 'Adventure', 'History'], 'months': 'November–April', 'highlights': ['Cellular Jail', "Corbyn's Cove", 'Ross Island boat trip']}, {'place': 'Srinagar', 'state': 'Jammu and Kashmir', 'region': 'North', 'stay': 1300, 'food': 700, 'local': 500, 'activities': 500, 'tags': ['Nature', 'Adventure', 'Snow'], 'months': 'April–October; winter for snow', 'highlights': ['Dal Lake', 'Mughal Gardens', 'Old Srinagar']}, {'place': 'Leh', 'state': 'Ladakh', 'region': 'North', 'stay': 1500, 'food': 750, 'local': 700, 'activities': 600, 'tags': ['Nature', 'Adventure', 'Snow'], 'months': 'May–September', 'highlights': ['Leh Palace', 'Shanti Stupa', 'Nubra Valley (permit/route dependent)']}, {'place': 'Kargil', 'state': 'Ladakh', 'region': 'North', 'stay': 1100, 'food': 650, 'local': 600, 'activities': 300, 'tags': ['Nature', 'Historical', 'Adventure'], 'months': 'May–September', 'highlights': ['Kargil War Memorial', 'Sur Valley', 'Local heritage sites']}]
COORDS = {'Amritsar': (31.634, 74.8723), 'Chandigarh': (30.7333, 76.7794), 'Shimla': (31.1048, 77.1734), 'Manali': (32.2432, 77.1892), 'Dharamshala and McLeod Ganj': (32.219, 76.3234), 'Kasol': (32.01, 77.315), 'Rishikesh': (30.0869, 78.2676), 'Haridwar': (29.9457, 78.1642), 'Nainital': (29.3803, 79.4636), 'Jaipur': (26.9124, 75.7873), 'Udaipur': (24.5854, 73.7125), 'Jodhpur': (26.2389, 73.0243), 'Jaisalmer': (26.9157, 70.9083), 'Pushkar': (26.4899, 74.5511), 'Ujjain': (23.1793, 75.7849), 'Mandu': (22.3333, 75.4), 'Maheshwar': (22.1759, 75.587), 'Bhopal': (23.2599, 77.4126), 'Pachmarhi': (22.4674, 78.433), 'Khajuraho': (24.8318, 79.9199), 'Orchha': (25.3519, 78.6407), 'Varanasi': (25.3176, 82.9739), 'Agra': (27.1767, 78.0081), 'Lucknow': (26.8467, 80.9462), 'Mumbai': (19.076, 72.8777), 'Pune': (18.5204, 73.8567), 'Nashik': (19.9975, 73.7898), 'Mahabaleshwar': (17.9307, 73.6477), 'Goa': (15.2993, 74.124), 'Ahmedabad': (23.0225, 72.5714), 'Rann of Kutch': (23.7337, 69.8597), 'Diu': (20.7141, 70.9874), 'Hyderabad': (17.385, 78.4867), 'Hampi': (15.335, 76.46), 'Bengaluru': (12.9716, 77.5946), 'Mysuru': (12.2958, 76.6394), 'Coorg': (12.3375, 75.8069), 'Gokarna': (14.5479, 74.3188), 'Chennai': (13.0827, 80.2707), 'Ooty': (11.4064, 76.6932), 'Kodaikanal': (10.2381, 77.4892), 'Madurai': (9.9252, 78.1198), 'Rameswaram': (9.2876, 79.3129), 'Kochi': (9.9312, 76.2673), 'Munnar': (10.0889, 77.0595), 'Alappuzha': (9.4981, 76.3388), 'Varkala': (8.7379, 76.7163), 'Puducherry': (11.9416, 79.8083), 'Kolkata': (22.5726, 88.3639), 'Darjeeling': (27.041, 88.2663), 'Gangtok': (27.3389, 88.6065), 'Shillong': (25.5788, 91.8933), 'Cherrapunji (Sohra)': (25.2702, 91.7323), 'Kaziranga': (26.5775, 93.1711), 'Guwahati': (26.1445, 91.7362), 'Tawang': (27.586, 91.8594), 'Puri': (19.8135, 85.8312), 'Bhubaneswar': (20.2961, 85.8245), 'Ranchi': (23.3441, 85.3096), 'Raipur': (21.2514, 81.6296), 'Visakhapatnam': (17.6868, 83.2185), 'Araku Valley': (18.3273, 82.8775), 'Port Blair (Sri Vijaya Puram)': (11.6234, 92.7265), 'Srinagar': (34.0837, 74.7973), 'Leh': (34.1526, 77.5771), 'Kargil': (34.5539, 76.1349)}
REGIONS = ["North","Central","West","South","East","Islands"]
TAGS = sorted({tag for d in DESTINATIONS for tag in (d.get("tags") or [])})

st.markdown("""
<style>
.stApp {{background:linear-gradient(135deg,#071b2b 0%,#102f3d 55%,#173b42 100%);}}
.block-container {{max-width:1250px;padding-top:1.4rem;}}
.hero {{padding:25px;border:1px solid #42616a;border-radius:18px;background:rgba(255,255,255,.07);}}
div.stButton>button {{background:#0da8c9;color:white;border:0;border-radius:9px;font-weight:650;}}
.smallnote {{padding:12px;border-left:4px solid #0da8c9;background:rgba(255,255,255,.07);}}
</style>
""", unsafe_allow_html=True)

def maps_url(place):
    return "https://www.google.com/maps/search/?api=1&query="+quote_plus(place+", India")

def weather_for(place):
    lat,lon=COORDS[place]
    params={{"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max","timezone":"auto","forecast_days":7}}
    r=requests.get("https://api.open-meteo.com/v1/forecast",params=params,timeout=15); r.raise_for_status()
    return r.json()

def wx(code):
    return {{0:"Clear",1:"Mostly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",48:"Rime fog",51:"Drizzle",53:"Drizzle",55:"Heavy drizzle",
    61:"Light rain",63:"Rain",65:"Heavy rain",71:"Light snow",73:"Snow",75:"Heavy snow",80:"Showers",81:"Showers",82:"Heavy showers",
    95:"Thunderstorm",96:"Thunderstorm with hail",99:"Severe thunderstorm"}}.get(code,"Variable conditions")

def estimate(d, days, people, comfort, fare_pp):
    mult=1.35 if comfort=="Comfortable" else 1.0
    stay=round(d["stay"]*days*mult)*people
    food=round(d["food"]*days*(1.15 if comfort=="Comfortable" else 1.0))*people
    local=d["local"]*days*people
    activities=d["activities"]*days*people
    intercity=fare_pp*people
    return {{"stay":stay,"food":food,"local":local,"activities":activities,"intercity":intercity,"total":stay+food+local+activities+intercity}}

def itinerary_for(d, days):
    h=d["highlights"]
    return [{{"day":i+1,"morning":h[(2*i)%len(h)],"afternoon":h[(2*i+1)%len(h)],"evening":h[(2*i+2)%len(h)]}} for i in range(days)]

def make_pdf(title, lines):
    buff=io.BytesIO()
    doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=38,leftMargin=38,topMargin=40,bottomMargin=40)
    styles=getSampleStyleSheet(); story=[Paragraph(title,styles["Title"]),Spacer(1,12)]
    for line in lines:
        story.append(Paragraph(str(line).replace("&","&amp;"),styles["BodyText"])); story.append(Spacer(1,7))
    doc.build(story); return buff.getvalue()

st.markdown('<div class="hero">',unsafe_allow_html=True)
st.title("🧭 TrekVerse V6 — The India Travel Command Centre")
st.write("Discover places, compare budgets, plan multi-stop journeys, check weather, map destinations and export a travel booklet.")
st.caption("One consolidated release • 66 destinations • Free/open tools • No paid AI API key")
st.markdown('</div>',unsafe_allow_html=True)

with st.sidebar:
    st.header("Trip controls")
    origin=st.text_input("Starting city","Indore")
    budget=st.number_input("Total group budget (₹)",500,1000000,10000,500)
    people=st.number_input("Travellers",1,30,2)
    days=st.slider("Days per destination",1,14,2)
    month=st.selectbox("Travel month",["January","February","March","April","May","June","July","August","September","October","November","December"],index=10)
    interests=st.multiselect("Interests",TAGS,default=["Nature","Historical"])
    comfort=st.selectbox("Travel style",["Budget","Comfortable"])
    fare_pp=st.number_input("Round-trip intercity fare per person (₹)",0,200000,0,250)
    regions=st.multiselect("Regions",REGIONS,default=REGIONS)
    st.caption("Enter a checked fare. The app cannot verify live ticket prices.")

per_person=budget/people
m1,m2,m3,m4=st.columns(4)
m1.metric("Group budget",f"₹{budget:,}")
m2.metric("Travellers",people)
m3.metric("Days / stop",days)
m4.metric("Per-person budget",f"₹{per_person:,.0f}")

# Recommendation engine
matches=[]
for d in DESTINATIONS:
    if d["region"] not in regions: continue
    cost=estimate(d,days,people,comfort,fare_pp)
    if cost["total"]<=budget:
        score=len(set(interests)&set(d["tags"]))*4 + (2 if cost["total"]<budget*.75 else 0)
        matches.append((score,cost["total"],d,cost))
matches.sort(key=lambda x:(x[0],-x[1]),reverse=True)

tabs=st.tabs(["✨ Discover & Budget","🗓️ Itinerary Studio","🧭 Multi-city Route","🗺️ Map","🌤️ Weather","🤖 Travel Chat","❤️ Saved Places","🧰 Admin & Data","🎒 Trip Toolkit"])

with tabs[0]:
    st.header("Destinations that fit your budget")
    st.caption(f"Planning from {origin}. Estimates are illustrative; intercity fare uses your sidebar input.")
    if not matches: st.warning("No destination fits these inputs. Increase budget, reduce days/people, or adjust regions/interests.")
    for score,total,d,cost in matches[:20]:
        with st.expander(f"📍 {d['place']}, {d['state']} — ₹{total:,} estimated group total"):
            st.write("**Highlights:** "+", ".join(d["highlights"]))
            st.write(f"**Region:** {d['region']} | **Best season:** {d['months']} | **Tags:** {', '.join(d['tags'])}")
            cols=st.columns(6)
            for col,(label,key) in zip(cols,[("Stay","stay"),("Food","food"),("Local","local"),("Activities","activities"),("Intercity","intercity"),("Total","total")]):
                col.metric(label,f"₹{cost[key]:,}")
            st.write(f"**Remaining budget:** ₹{budget-total:,}")
            st.link_button("Open on Google Maps",maps_url(d["place"]))
            if st.button("♡ Save destination",key="save_"+d["place"]):
                saved=st.session_state.get("saved_places",[])
                if d["place"] not in saved: saved.append(d["place"])
                st.session_state.saved_places=saved
                st.success("Saved to your favourites.")
    if matches:
        df=pd.DataFrame([{{"Destination":d["place"],"State":d["state"],"Group estimate (₹)":c["total"],"Remaining (₹)":budget-c["total"],"Best season":d["months"]}} for _,_,d,c in matches])
        st.download_button("Download comparison CSV",df.to_csv(index=False).encode(), "trekverse_comparison.csv","text/csv")

with tabs[1]:
    st.header("Day-wise itinerary studio")
    choices=[d for _,_,d,_ in matches] or DESTINATIONS
    chosen=st.selectbox("Choose destination",[d["place"] for d in choices],key="itin_place")
    d=next(x for x in DESTINATIONS if x["place"]==chosen)
    plan=itinerary_for(d,days)
    cost=estimate(d,days,people,comfort,fare_pp)
    st.subheader(f"{days}-day plan: {d['place']}")
    st.info("This is a sample schedule based on known highlights. Check distances, opening hours, tickets and local access before following it.")
    for p in plan:
        with st.expander(f"Day {p['day']}",expanded=p["day"]==1):
            st.write(f"**Morning:** {p['morning']}")
            st.write(f"**Afternoon:** {p['afternoon']}")
            st.write(f"**Evening:** {p['evening']}")
            st.write("Leave time for meals, rest and travel between sites.")
    st.subheader("Estimated group budget")
    cc=st.columns(6)
    for col,(label,key) in zip(cc,[("Stay","stay"),("Food","food"),("Local","local"),("Activities","activities"),("Intercity","intercity"),("Total","total")]):
        col.metric(label,f"₹{cost[key]:,}")
    pdf_lines=[f"Starting city: {origin}",f"Destination: {d['place']}, {d['state']}",f"Travellers: {people}; Days: {days}; Month: {month}",
               "Highlights: "+", ".join(d["highlights"])]
    for p in plan: pdf_lines.append(f"Day {p['day']}: Morning {p['morning']}; Afternoon {p['afternoon']}; Evening {p['evening']}.")
    pdf_lines += [f"Accommodation estimate: ₹{cost['stay']}",f"Food estimate: ₹{cost['food']}",f"Local transport estimate: ₹{cost['local']}",
                  f"Activities estimate: ₹{cost['activities']}",f"Intercity transport estimate: ₹{cost['intercity']}",f"Total estimate: ₹{cost['total']}",
                  "All prices are planning estimates, not live quotes."]
    st.download_button("📘 Download printable PDF travel booklet",make_pdf("TrekVerse Travel Plan",pdf_lines),
                       file_name=f"trekverse_{d['place'].lower().replace(' ','_')}.pdf",mime="application/pdf")
    st.download_button("Download itinerary CSV",pd.DataFrame(plan).to_csv(index=False).encode(),"trekverse_itinerary.csv","text/csv")

with tabs[2]:
    st.header("Multi-city journey planner")
    st.write("Build a sequence of stops. The tool totals destination-day estimates; add intercity fare estimates for the full route.")
    allnames=[d["place"] for d in DESTINATIONS]
    route=st.multiselect("Select stops in the order you want to visit",allnames,default=[x for x in ["Ujjain","Jaipur"] if x in allnames],max_selections=8)
    route_days=st.number_input("Days at each stop",1,14,2,key="route_days")
    route_fare=st.number_input("Estimated total intercity transport for entire group (₹)",0,500000,0,500,key="route_fare")
    if route:
        route_rows=[]; total_dest=0
        for place in route:
            item=next(x for x in DESTINATIONS if x["place"]==place)
            c=estimate(item,route_days,people,comfort,0)
            total_dest+=c["total"]
            route_rows.append({{"Stop":place,"State":item["state"],"Days":route_days,"Estimated stay+food+local+activities (₹)":c["total"]}})
        grand=total_dest+route_fare
        st.dataframe(pd.DataFrame(route_rows),use_container_width=True,hide_index=True)
        st.metric("Estimated total route cost",f"₹{grand:,}")
        st.metric("Budget remaining / overrun",f"₹{budget-grand:,}")
        if grand>budget: st.warning("This route is over budget based on your estimates.")
        else: st.success("This route fits your entered budget based on your estimates.")
        st.link_button("Open route search in Google Maps","https://www.google.com/maps/dir/"+"/".join(quote_plus(x+", India") for x in [origin]+route))
        st.download_button("Download multi-city route CSV",pd.DataFrame(route_rows).to_csv(index=False).encode(),"trekverse_multi_city.csv","text/csv")
    else: st.info("Choose at least one stop.")

with tabs[3]:
    st.header("Interactive destination map")
    map_places=[d for d in DESTINATIONS if d["region"] in regions]
    mp=folium.Map(location=[22.5,79],zoom_start=4,tiles="OpenStreetMap")
    for d in map_places:
        lat,lon=COORDS[d["place"]]
        folium.Marker([lat,lon],tooltip=d["place"],popup=f"{d['place']}, {d['state']}").add_to(mp)
    st_folium(mp,height=500,width=None,returned_objects=[])
    st.caption("Pins mark approximate city/destination centres, not every attraction.")

with tabs[4]:
    st.header("Live weather forecast")
    wp=st.selectbox("Destination for weather",[d["place"] for d in DESTINATIONS],key="weather_place")
    if st.button("Fetch 7-day forecast"):
        try:
            with st.spinner("Contacting Open-Meteo..."): w=weather_for(wp)
            cur=w["current"]
            a,b,c,e=st.columns(4)
            a.metric("Temperature",f"{{cur['temperature_2m']}} °C")
            b.metric("Feels like",f"{{cur['apparent_temperature']}} °C")
            c.metric("Humidity",f"{{cur['relative_humidity_2m']}}%")
            e.metric("Wind",f"{{cur['wind_speed_10m']}} km/h")
            daily=w["daily"]
            weather_df=pd.DataFrame({{"Date":daily["time"],"Weather":[wx(x) for x in daily["weather_code"]],
                "Min °C":daily["temperature_2m_min"],"Max °C":daily["temperature_2m_max"],
                "Rain chance %":daily["precipitation_probability_max"]}})
            st.dataframe(weather_df,use_container_width=True,hide_index=True)
            st.caption("Open-Meteo forecast; recheck before travel. Weather is not a safety guarantee.")
        except Exception as ex: st.error(f"Weather service unavailable: {{ex}}")
    st.link_button("Open this destination in Google Maps",maps_url(wp))

with tabs[5]:
    st.header("Travel chat assistant")
    st.caption("Free local rule-based helper; it is not a generative LLM.")
    if "chat" not in st.session_state:
        st.session_state.chat=[("assistant","Hi! Tell me your budget, days and interests. Example: ₹5000 for 2 days, nature, from Indore.")]
    for role,msg in st.session_state.chat:
        with st.chat_message(role): st.markdown(msg)
    prompt=st.chat_input("Ask TrekVerse...")
    if prompt:
        st.session_state.chat.append(("user",prompt))
        q=prompt.lower()
        dm=re.search(r"(\d[\d,]*)\s*(k)?",q)
        cb=int(dm.group(1).replace(",",""))*(1000 if dm and dm.group(2) else 1) if dm else budget
        daym=re.search(r"(\d+)\s*days?",q); nd=int(daym.group(1)) if daym else days
        wanted=[t for t in TAGS if t.lower() in q]
        cand=[]
        for dest in DESTINATIONS:
            if dest["region"] not in regions or (wanted and not set(wanted)&set(dest["tags"])): continue
            est=estimate(dest,max(1,min(nd,14)),people,comfort,fare_pp)
            if est["total"]<=cb: cand.append((est["total"],dest,est))
        cand.sort(key=lambda x:x[0])
        if cand:
            answer=f"For about ₹{{cb:,}}, here are options for {{nd}} day(s):\n\n"+ "\n".join(
                f"- **{{dest['place']}}, {{dest['state']}}** — estimate ₹{{est['total']:,}}. Highlights: {{', '.join(dest['highlights'][:2])}}."
                for _,dest,est in cand[:5])
            if fare_pp==0: answer+="\n\nNote: your intercity fare is set to zero, so travel from the origin is excluded."
            answer+="\n\nThese are estimates, not live prices."
        else:
            answer="I couldn't find a match in the current data. Try a higher budget, fewer days or different interests. Enter a checked return fare in the sidebar."
        st.session_state.chat.append(("assistant",answer))
        st.rerun()
    if st.button("Clear conversation"): st.session_state.chat=[]; st.rerun()

with tabs[6]:
    st.header("Saved places & favourites")
    if "saved_places" not in st.session_state: st.session_state.saved_places=[]
    saved=st.session_state.saved_places
    if saved:
        for name in saved:
            dest=next((x for x in DESTINATIONS if x["place"]==name),None)
            if dest:
                st.write(f"❤️ **{{name}}**, {{dest['state']}} — "+", ".join(dest["highlights"]))
                st.link_button(f"Map: {{name}}",maps_url(name),key="map_saved_"+name)
        if st.button("Clear favourites"): st.session_state.saved_places=[]; st.rerun()
        st.download_button("Export favourites CSV",pd.DataFrame({{"Favourite":saved}}).to_csv(index=False).encode(),"trekverse_favourites.csv","text/csv")
    else: st.info("Save destinations from the Discover tab. Favourites remain in this browser session; they are not a permanent user account.")

with tabs[7]:
    st.header("Admin tools & destination data")
    st.write("Download the built-in destination database, or upload a CSV to review extra destination records for your own planning.")
    base_df=pd.DataFrame([{{"place":d["place"],"state":d["state"],"region":d["region"],"stay_per_day":d["stay"],
        "food_per_day":d["food"],"local_per_day":d["local"],"activities_per_day":d["activities"],
        "tags":";".join(d["tags"]),"highlights":";".join(d["highlights"]),"best_season":d["months"]}} for d in DESTINATIONS])
    st.download_button("Download destination database CSV",base_df.to_csv(index=False).encode(),"trekverse_destination_database.csv","text/csv")
    upload=st.file_uploader("Upload destination CSV (preview only)",type=["csv"])
    if upload:
        try:
            user_df=pd.read_csv(upload)
            st.dataframe(user_df,use_container_width=True)
            st.info("This upload is preview-only; it does not overwrite the live database. Edit app.py to permanently add destinations.")
        except Exception as ex: st.error(f"Could not read CSV: {{ex}}")
    st.warning("This is a local admin/data utility, not a secure multi-user admin login. Do not store private data here.")

with tabs[8]:
    st.header("Trip preparation toolkit")
    st.subheader("Checklist")
    tasks=["Confirm return transport","Confirm accommodation and cancellation terms","Check weather and local warnings",
           "Check attraction opening hours and entry fees","Check permits and local access restrictions",
           "Carry valid ID and required documents","Save offline maps and emergency contacts",
           "Keep emergency money separate","Share itinerary with a trusted person","Pack medicines, chargers and suitable clothing"]
    done=[]
    cols=st.columns(2)
    for i,t in enumerate(tasks):
        with cols[i%2]:
            if st.checkbox(t,key="task_"+str(i)): done.append(t)
    st.progress(len(done)/len(tasks),text=f"{{len(done)}} / {{len(tasks)}} completed")
    st.download_button("Download checklist",pd.DataFrame({{"Completed task":done}}).to_csv(index=False).encode(),"trekverse_checklist.csv","text/csv")
    st.subheader("Useful emergency and travel links")
    st.write("India emergency response number: **112**. For immediate danger, contact local emergency services.")
    st.link_button("India emergency response (112)", "https://112.gov.in/")
    st.link_button("IRCTC train booking","https://www.irctc.co.in/")
    st.link_button("Bus search","https://www.redbus.in/")
    st.link_button("Flight search","https://www.google.com/travel/flights")
    st.link_button("Hotel search","https://www.google.com/travel/hotels")
    st.link_button("Incredible India destination information","https://www.incredibleindia.gov.in/")
    st.link_button("Google Maps","https://www.google.com/maps")

st.divider()
st.caption("TrekVerse V6 • Built with Python, Streamlit, Pandas, Folium, OpenStreetMap, Open-Meteo and ReportLab.")
st.caption("Critical limitations: estimates are illustrative, maps use approximate pins, weather depends on an external service, booking links are external, and no ticket/hotel booking or availability is confirmed. Chat is rule-based, not a generative AI model. Verify all details before spending money.")
