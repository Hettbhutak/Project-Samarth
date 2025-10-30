import requests
import pandas as pd
import json
from typing import Dict, Any, Optional

class DataGovCollector:
    def __init__(self):
        self.base_url = "https://api.data.gov.in/resource"
        self.api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
        
    def fetch_agriculture_data(self) -> Optional[Dict[str, Any]]:
        """Fetch agriculture data using direct resource ID"""
        try:
            # Example resource ID for agriculture data
            resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "offset": 0,
                "limit": 100
            }
            url = f"{self.base_url}/{resource_id}"
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching agriculture data: {e}")
            return None

    def fetch_climate_data(self) -> Optional[Dict[str, Any]]:
        """Fetch climate data using direct resource ID"""
        try:
            # Example resource ID for rainfall data
            resource_id = "102a9f85-9ccf-4c87-a22f-44780c596027"
            params = {
                "api-key": self.api_key,
                "format": "json",
                "offset": 0,
                "limit": 100
            }
            url = f"{self.base_url}/{resource_id}"
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching climate data: {e}")
            return None

if __name__ == "__main__":
    collector = DataGovCollector()
    
    print("Fetching agriculture data...")
    agri_data = collector.fetch_agriculture_data()
    if agri_data:
        print(f"Successfully fetched agriculture data")
        print(f"Records found: {len(agri_data.get('records', []))}")
    
    print("\nFetching climate data...")
    climate_data = collector.fetch_climate_data()
    if climate_data:
        print(f"Successfully fetched climate data")
        print(f"Records found: {len(climate_data.get('records', []))}")