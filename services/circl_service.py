import requests

CIRCL_URL = "https://cve.circl.lu/api/last"

def get_latest_circl():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        r = requests.get(CIRCL_URL, headers=headers, timeout=15)

        if r.status_code == 200:
            data = r.json()
            # Return Raw List langsung
            if isinstance(data, list):
                return data
            
        return []
    except Exception:
        return []