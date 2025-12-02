import requests

CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

def get_cisa_alerts():
    try:
        r = requests.get(CISA_URL, timeout=10)
        if r.status_code != 200:
            return []

        data = r.json()
        
        return data.get("vulnerabilities", [])
    except Exception:
        return []