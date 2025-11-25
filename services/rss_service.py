import feedparser

RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://threatpost.com/feed/"
]

def get_rss_threats():
    results = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:3]:
                results.append({
                    "source": "RSS",
                    "title": entry.title,
                    "description": entry.summary if hasattr(entry, "summary") else "",
                    "link": entry.link
                })

        except Exception:
            continue

    return results
