from dotenv import load_dotenv
import os
import requests
import pandas as pd

load_dotenv()
census_key = os.getenv("CENSUS_API_KEY")

YEAR = 2019
base_url = f"https://api.census.gov/data/{YEAR}/pep/population"

def get_population(tract, state, county):
    params = {
        "get": "B01003_001E",
        "for": f"tract:{tract}", 
        "in": f"state:{state}+county:{county}",
        "key": census_key
    }

    response = requests.get(base_url, params)

    if response.status_code == 200:
        data = response.json()
    else:
        print("Error:", response.status_code)
    
    return data

