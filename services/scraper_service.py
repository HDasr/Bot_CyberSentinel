import requests
from bs4 import BeautifulSoup

SCRAPE_URL = "https://thehackernews.com/"

def get_scraped_threats():
    try:
        # User-Agent header agar tidak dianggap bot oleh server
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        html = requests.get(SCRAPE_URL, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # PERBAIKAN 1: Gunakan selector 'a.story-link' 
        # Ini menargetkan tag <a> pembungkus artikel secara langsung
        articles = soup.select("a.story-link")[:5] # Ambil 5 biar aman

        results = []
        for a in articles:
            # PERBAIKAN 2: Ambil atribut 'href' langsung dari elemen <a>
            link = a.get('href')

            # Title dan Desc ada di dalam elemen <a> tersebut
            title_elm = a.select_one(".home-title")
            desc_elm = a.select_one(".home-desc")

            # Gunakan if/else untuk mencegah error jika elemen tidak ketemu
            title = title_elm.text.strip() if title_elm else "No Title"
            desc = desc_elm.text.strip() if desc_elm else "No Description"

            results.append({
                "source": "SCRAPER",
                "title": title,
                "description": desc,
                "link": link, # <--- Bagian ini yang sebelumnya hilang
                "cvss": None  # Tambahkan placeholder CVSS agar konsisten
            })

        return results

    except Exception as e:
        # Print error di console biar ketahuan kalau ada masalah
        print(f"[Scraper Error] {e}")
        return []