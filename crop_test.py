# requirements: pip install requests pandas duckdb
import requests
import pandas as pd
import duckdb
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"

# Updated resource IDs for more reliable datasets
RAINFALL_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Example resource ID
CROP_RESOURCE_ID = "6d25a34f-7874-4501-87ea-913d7b6021c4"      # Example resource ID

def create_robust_session():
    """Create a session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def fetch_resource(resource_id, api_key, limit=1000):
    """Fetch data with improved error handling and retry logic"""
    session = create_robust_session()
    
    try:
        # First try the newer API endpoint
        url = f"https://api.data.gov.in/resource/{resource_id}"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": limit,
            "offset": 0
        }
        
        print(f"Fetching data from {url}")
        r = session.get(url, params=params, timeout=60)
        r.raise_for_status()
        
        data = r.json()
        records = data.get("records", [])
        
        if not records and "result" in data:
            records = data["result"].get("records", [])
        
        if not records:
            print(f"No records found in response. Response structure: {list(data.keys())}")
            return pd.DataFrame()
            
        return pd.DataFrame.from_records(records)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching resource {resource_id}: {str(e)}")
        return pd.DataFrame()

def main():
    # 1) Fetch datasets with progress indication
    print("Fetching rainfall data...")
    rain_df = fetch_resource(RAINFALL_RESOURCE_ID, API_KEY)
    if not rain_df.empty:
        print(f"Successfully fetched rainfall data: {len(rain_df)} rows")
    
    print("\nFetching crop data...")
    crop_df = fetch_resource(CROP_RESOURCE_ID, API_KEY)
    if not crop_df.empty:
        print(f"Successfully fetched crop data: {len(crop_df)} rows")
    
    # 2) Save raw data to CSV for inspection
    if not rain_df.empty:
        rain_df.to_csv('rainfall_data.csv', index=False)
        print("Saved rainfall data to rainfall_data.csv")
    
    if not crop_df.empty:
        crop_df.to_csv('crop_data.csv', index=False)
        print("Saved crop data to crop_data.csv")
    
    # 3) Display basic information about the datasets
    if not rain_df.empty:
        print("\nRainfall Data Info:")
        print("Columns:", rain_df.columns.tolist())
        print("Sample data:")
        print(rain_df.head())
    
    if not crop_df.empty:
        print("\nCrop Data Info:")
        print("Columns:", crop_df.columns.tolist())
        print("Sample data:")
        print(crop_df.head())

if __name__ == "__main__":
    main()

# 4) Store into DuckDB for quick SQL queries
con = duckdb.connect(':memory:')
con.register('rain_df', rain_df)
con.register('crop_df', crop_df)

# Example SQL: avg rainfall last 5 years for two states
sql = """
SELECT state, AVG(annual_mm) AS avg_rain
FROM rain_df
WHERE year >= (SELECT MAX(year) FROM rain_df) - 4
  AND state IN ('State_X','State_Y')
GROUP BY state
"""
try:
    print(con.execute(sql).fetchdf())
except Exception as e:
    print("SQL example failed (adjust column names):", e)
