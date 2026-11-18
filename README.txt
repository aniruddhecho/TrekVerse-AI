# TrekVerse AI Travel Assistant (free beginner starter)

This project recreates the main idea in your photo: a travel assistant plus a trip-planning form.

## What it does
- Takes total budget, number of travellers, days, month and interests.
- Recommends destinations from a small built-in India destination list.
- Estimates a rough group cost and remaining budget.
- Lets you download recommendations as CSV.
- Runs locally on your Windows PC.

## Important honesty note
This is a **rule-based travel recommender**, not a large language model. It uses Python rules and a small sample dataset, so it needs no paid AI API, API key, or subscription. A truly generative chatbot normally needs either a hosted model/API (which may cost money) or a local model (free software, but requires a capable computer and disk space).

The sample transport estimates are based on an example journey from Indore and are not live fares. Replace them with current prices before relying on them. The list is intentionally small so a beginner can understand and edit it.

## Install on Windows 11
1. Install Python 3.11 or newer from https://www.python.org/downloads/ . During setup, tick **Add Python to PATH**.
2. Install Visual Studio Code from https://code.visualstudio.com/ .
3. Open VS Code. Choose **File > Open Folder** and open this `TrekVerse_AI_Travel_Planner` folder.
4. In VS Code choose **Terminal > New Terminal**.
5. Run these commands one at a time:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

6. A browser tab should open. If it does not, copy the local address shown in the terminal (usually `http://localhost:8501`) into your browser.
7. To stop the app, click the terminal and press **Ctrl + C**.

## Every time you want to open it again
1. Open the project folder in VS Code.
2. Open **Terminal > New Terminal**.
3. Run:

```powershell
.venv\Scripts\activate
py -m streamlit run app.py
```

## If PowerShell blocks activation
Use Command Prompt terminal instead, or run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## How to change destinations and prices
Open `app.py` and find `PLACES = [`.
Each destination has:
- `travel`: rough round-trip transport estimate per person from Indore
- `stay`: accommodation estimate per person for the listed typical trip length
- `food`: food estimate per person for the listed typical trip length
- `local`: local transport estimate per person for the listed typical trip length
- `days`: typical trip duration
- `tags`: interests used by the recommendation rules

Edit those values using prices you have checked. Save the file; Streamlit will refresh.

## Free resources
- Python: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/
- Streamlit install guide: https://docs.streamlit.io/get-started/installation
- Streamlit Community Cloud (optional public hosting): https://streamlit.io/cloud
- Open-Meteo (optional weather upgrade; free non-commercial use, no API key, attribution required): https://open-meteo.com/

No API key is required for this starter app.
