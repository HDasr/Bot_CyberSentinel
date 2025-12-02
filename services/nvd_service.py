import requests
import os
from config import NVD_API_URL, NVD_API

def get_latest_nvd():
    try:
        headers = {
            "apiKey": NVD_API,
            "User-Agent": "CyberSentinel-Bot/1.0"
        }
        
        params = {
            "resultsPerPage": 20,
            "startIndex": 0
        }

        response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=20)
        
        if response.status_code != 200:
            print(f"NVD Error: {response.status_code}")
            return []
        
        data = response.json()
        return data.get("vulnerabilities", []) 
    except Exception as e:
        print(f"NVD Exception: {e}")
        return []