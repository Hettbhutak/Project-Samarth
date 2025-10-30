# Project Samarth - Agricultural Q&A & Analytics Platform

Project Samarth is an interactive web app for exploring Indian agricultural trends, state-wise rainfall, and crop production data through natural language questions.

## ✨ Features
- **Ask questions** about crop yield and rainfall statistics in simple English.
- **Compare states:** "Compare rainfall for Gujarat and Maharashtra in 2022."
- **See top crops:** "What were the top crops in Karnataka last 3 years?"
- **Modern UI:** Responsive and user-friendly, designed for all devices.
- **Clickable suggestions:** Instantly see the app in action with sample queries.

## 🏗️ How it Works
- Powered by [Streamlit](https://streamlit.io/) and Python (see `requirements.txt`).
- All data is loaded from local CSV files (`rainfall_data.csv`, `crop_yield.csv`).
- **You can use your own CSVs** by replacing/editing these files!

## 🚀 Getting Started Locally
1. **Clone this repo:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```
2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   streamlit run app.py
   ```
4. Go to the URL (default: [localhost:8501](http://localhost:8501))

## 📊 Data
- Sample data is included for demo: `rainfall_data.csv` (rainfall stats) and `crop_yield.csv` (crop-wise state stats).
- You can add new years, states, or crops by editing these CSVs.

## 🙌 Credits
- Data sources: Open Government Data (data.gov.in), India Meteorological Department, Ministry of Agriculture, benchmark open datasets
- App design, engineering: Racila Softecch

---
_Reach out if you want to extend the dataset or add new analysis features!_
