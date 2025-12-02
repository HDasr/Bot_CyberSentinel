import requests
from bs4 import BeautifulSoup

SCRAPE_URL = "https://thehackernews.com/"

def get_scraped_threats():
    try:
        # User-Agent header agar tidak dianggap bot
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        html = requests.get(SCRAPE_URL, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        all_articles = soup.select("a.story-link") 

        results = []
        
        for a in all_articles:
            if len(results) >= 5:
                break

            link = a.get('href')
            
            if not link:
                continue
                
            if "thehackernews.com" not in link:
                continue
            
            title_elm = a.select_one(".home-title")
            desc_elm = a.select_one(".home-desc")

            title = title_elm.text.strip() if title_elm else "No Title"
            desc = desc_elm.text.strip() if desc_elm else "No Description"

            results.append({
                "source": "SCRAPER",
                "title": title,
                "description": desc,
                "link": link,
                "cvss": None
            })

        return results

    except Exception as e:
        print(f"[Scraper Error] {e}")
        return []