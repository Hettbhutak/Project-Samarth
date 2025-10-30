# qa_engine.py
import requests
import pandas as pd
import duckdb
import re
import json
API_KEY = "579b464db66ec23bdd000001eda4e5e8416a4ed1580558119b11c1cc"  # <-- replace with your actual data.gov.in API key

# Load dataset metadata
with open("datasets_info.json") as f:
    DATASETS = json.load(f)

def fetch_resource(resource_id, limit=10000):
    """Fetch dataset from data.gov.in using API or local file for crop data"""
    # Use the correct key for crop data
    crop_resource_id = DATASETS["crop_production"]["resource_id"]
    rainfall_resource_id = DATASETS["rainfall"]["resource_id"]
    if resource_id == crop_resource_id:
        try:
            # Always load from crop_yield.csv for crop_production
            import os
            csv_path = os.path.join(os.path.dirname(__file__), "crop_yield.csv")
            data = pd.read_csv(csv_path)
            return data
        except Exception as e:
            print(f"Error loading crop_yield.csv: {e}")
            return pd.DataFrame()
    if resource_id == rainfall_resource_id:
        try:
            import os
            csv_path = os.path.join(os.path.dirname(__file__), "rainfall_data.csv")
            data = pd.read_csv(csv_path)
            return data
        except Exception as e:
            print(f"Error loading rainfall_data.csv: {e}")
            return pd.DataFrame()
    # Otherwise, use the API for other datasets
    url = f"https://api.data.gov.in/resource/{resource_id}"
    params = {"api-key": API_KEY, "format": "json", "limit": limit}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data["records"])

# ------------------ Normalization Helpers -------------------

def normalize_rainfall(df):
    """Convert monthly rainfall columns to annual"""
    df = df.rename(columns=str.lower)
    month_cols = [c for c in df.columns if any(m in c for m in [
        "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
    ])]
    if month_cols:
        for c in month_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["annual_mm"] = df[month_cols].sum(axis=1)
    if "state" not in df.columns:
        if "subdivision" in df.columns:
            df["state"] = df["subdivision"]
    df["year"] = pd.to_numeric(df["year"] if "year" in df.columns else df["yr"], errors="coerce")
    return df[["state", "year", "annual_mm"]].dropna()

def normalize_crop(df):
    """Standardize crop production data, accepting crop_yield.csv structure"""
    df = df.rename(columns=str.lower)
    # Use crop_year as year if year is missing
    if "year" not in df.columns and "crop_year" in df.columns:
        df["year"] = df["crop_year"]
    required_cols = ["state", "crop", "year", "production"]
    # Early exit if DataFrame is empty
    if df.empty:
        raise KeyError("Crop data file returned no records. Please check the CSV file and its path.")
    col_map = {
        "state": ["state", "subdivision"],
        "crop": ["crop", "commodity"],
        "year": ["year", "crop_year", "yr"],
        "production": ["production", "production_tonnes", "prod_tonnes", "modal_price", "max_price"]
    }
    for key, alternatives in col_map.items():
        for alt in alternatives:
            if alt in df.columns:
                df[key] = df[alt]
                break
    # If district exists, include it as a column
    if "district" in df.columns:
        required_cols.insert(1, "district")
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in crop data: {missing}. Available columns: {df.columns.tolist()}")
    df["production"] = pd.to_numeric(df["production"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df[required_cols].dropna()

# ------------------ Core Analytics -------------------

def compare_rainfall_and_crops(state_x, state_y, crop_type=None, years=5):
    rain = normalize_rainfall(fetch_resource(DATASETS["rainfall"]["resource_id"]))
    crop = normalize_crop(fetch_resource(DATASETS["crop_production"]["resource_id"]))

    con = duckdb.connect(":memory:")
    con.register("rain", rain)
    con.register("crop", crop)

    # Ensure rain['year'] is not empty/all-NA to avoid ValueError
    if rain["year"].dropna().empty:
        raise ValueError("Rainfall data contains no valid years. Please check your rainfall dataset.")
    max_year_value = rain["year"].max()
    if pd.isna(max_year_value):
        raise ValueError("Rainfall data has NaN as the maximum year. Please verify your data file.")
    max_year = int(max_year_value)
    min_year = max_year - years + 1

    rainfall_query = f"""
        SELECT state, AVG(annual_mm) AS avg_rain
        FROM rain
        WHERE year BETWEEN {min_year} AND {max_year}
          AND state IN ('{state_x}', '{state_y}')
        GROUP BY state
    """
    rainfall_df = con.execute(rainfall_query).fetchdf()

    crops_query = f"""
        SELECT state, crop, SUM(production) AS total_prod
        FROM crop
        WHERE year BETWEEN {min_year} AND {max_year}
          AND state IN ('{state_x}', '{state_y}')
        GROUP BY state, crop
        ORDER BY state, total_prod DESC
    """
    top_crops = con.execute(crops_query).fetchdf().groupby("state").head(3)

    citations = [
        f"{DATASETS['rainfall']['title']} (Source: {DATASETS['rainfall']['source']})",
        f"{DATASETS['crop_production']['title']} (Source: {DATASETS['crop_production']['source']})"
    ]

    summary = (
        f"Between {min_year}–{max_year}, average rainfall in {state_x} was "
        f"{rainfall_df[rainfall_df['state']==state_x]['avg_rain'].iloc[0]:.2f} mm, "
        f"while {state_y} had "
        f"{rainfall_df[rainfall_df['state']==state_y]['avg_rain'].iloc[0]:.2f} mm.\n\n"
        f"Top crops produced were:\n{top_crops.to_string(index=False)}"
    )

    return summary, rainfall_df, top_crops, citations

# ------------------ Question Router -------------------

def parse_question(question):
    import re
    question_lc = question.lower()
    # Get all states and crops from the data for matching
    try:
        all_states = set(pd.read_csv("crop_yield.csv")["State"].str.strip()) | set(pd.read_csv("rainfall_data.csv")["state"].str.strip())
    except Exception:
        all_states = {"Andhra Pradesh", "Gujarat", "Maharashtra", "Karnataka"}
    try:
        all_crops = set(pd.read_csv("crop_yield.csv")["Crop"].str.strip())
    except Exception:
        all_crops = {"Sugarcane", "Cotton(lint)", "Potato", "Soyabean", "Rice"}
    # Find up to 2 states in the question
    states_found = [s for s in all_states if s.lower() in question_lc]
    crops_found = [c for c in all_crops if c.lower() in question_lc]
    # Extract year(s): any 4-digit number
    year_matches = re.findall(r"(20\d{2}|19\d{2})", question)
    years_found = [int(y) for y in year_matches] if year_matches else []
    # Extract periods like 'last 5 years'
    n_years_match = re.search(r"last (\d+) years?", question_lc)
    n_years = int(n_years_match.group(1)) if n_years_match else None
    # Fallback logic
    state_x = states_found[0] if len(states_found) > 0 else "Gujarat"
    state_y = states_found[1] if len(states_found) > 1 else "Maharashtra"
    crop_type = crops_found[0] if crops_found else None
    # Priority: explicit years -> period -> default
    if len(years_found) >= 2:
        # Range like 2018-2022: use as window
        min_year, max_year = min(years_found), max(years_found)
        n_years = max_year - min_year + 1
    elif len(years_found) == 1:
        max_year = years_found[0]
        n_years = 1
    if n_years is None:
        n_years = 5
    return {
        "state_x": state_x,
        "state_y": state_y,
        "crop_type": crop_type,
        "years": n_years
    }

def answer_question(question):
    params = parse_question(question)
    ans, rain, crops, cites = compare_rainfall_and_crops(
        params["state_x"], params["state_y"], params["crop_type"], params["years"]
    )
    return ans, rain, crops, cites

class QAEngine:
    def process_question(self, question):
        return answer_question(question)


