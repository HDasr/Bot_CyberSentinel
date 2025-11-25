import requests

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5"

def get_latest_nvd():
    try:
        response = requests.get(NVD_URL, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        # Return Raw List, jangan diproses di sini
        return data.get("vulnerabilities", []) 
    except Exception:
        return []