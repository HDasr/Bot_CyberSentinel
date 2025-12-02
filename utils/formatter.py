import logging

def format_vulnerabilities(data: list, tag="Update") -> list:
    if not data:
        return ["No data available."]

    messages = []
    
    header = f"🔐 <b>{tag}</b>\nLatest cybersecurity threats detected:\n\n"
    current_msg = header
    
    MAX_LENGTH = 4000 

    for item in data:
        cve     = item.get("cve") or "N/A"
        title   = item.get("title") or "No Title"
        cvss    = item.get("cvss")
        desc    = item.get("description") or "No description."
        link    = item.get("link")
        source  = item.get("source", "Unknown")

        item_str = "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if cve != "N/A" and cve != "Unknown" and cve is not None:
            item_str += f"📌 <b>{cve}</b>"
            if title and title != cve: 
                item_str += f" — {title}"
            item_str += "\n"
        else:
            item_str += f"📢 <b>{title}</b>\n"

        if cvss:
            try:
                score = float(cvss)
                emoji = "🟢" if score < 4.0 else "🟡" if score < 7.0 else "🔴"
                item_str += f"⚠️ CVSS: <b>{score}</b> {emoji}\n"
            except:
                item_str += f"⚠️ Severity: <b>{cvss}</b>\n"
        
        item_str += f"📂 Source: {source}\n"
        
        desc_str = str(desc).replace("<", "&lt;").replace(">", "&gt;")
        if len(desc_str) > 300:
            desc_str = desc_str[:300] + "..."
        item_str += f"📝 <i>{desc_str}</i>\n"

        if link and str(link).startswith("http"):
            item_str += f"🔗 <a href='{link}'>Read More</a>\n"
        
        item_str += "\n"

        if len(current_msg) + len(item_str) > MAX_LENGTH:
            messages.append(current_msg)
            current_msg = f"🔐 <b>{tag} (Continued...)</b>\n\n" + item_str
        else:
            current_msg += item_str

    if current_msg:
        messages.append(current_msg + "━━━━━━━━━━━━━━━━━━━━━━")

    return messages


def standardize_data(source_name: str, raw_data) -> list:
    if not raw_data:
        return []

    if source_name == "NVD":
        return normalize_nvd(raw_data)
    elif source_name == "CISA":
        return normalize_cisa(raw_data)
    elif source_name == "RSS":
        return normalize_rss(raw_data)
    elif source_name == "Scraper":
        return normalize_scraper(raw_data)
    else:
        return []


def normalize_nvd(data) -> list:
    results = []
    for entry in data:
        cve_obj = entry.get("cve", {})
        cve_id = cve_obj.get("id", "Unknown")
        descriptions = cve_obj.get("descriptions", [])
        desc_text = "No description."
        if descriptions:
            desc_text = next((d["value"] for d in descriptions if d["lang"] == "en"), descriptions[0].get("value"))
        metrics = cve_obj.get("metrics", {})
        cvss_score = None
        for ver in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if ver in metrics and metrics[ver]:
                cvss_data = metrics[ver][0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                break
        link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        results.append({
            "source": "NVD",
            "cve": cve_id,
            "title": cve_id,
            "description": desc_text,
            "cvss": cvss_score,
            "link": link
        })
    return results

def normalize_cisa(data) -> list:
    results = []
    for item in data:
        results.append({
            "source": "CISA KEV",
            "cve": item.get("cveID"),
            "title": item.get("vulnerabilityName"),
            "description": item.get("shortDescription"),
            "cvss": "CRITICAL",
            "link": f"https://nvd.nist.gov/vuln/detail/{item.get('cveID')}"
        })
    return results

def normalize_rss(data) -> list:
    results = []
    for item in data:
        results.append({
            "source": "RSS Feed",
            "cve": None,
            "title": item.get("title"),
            "description": item.get("description"),
            "cvss": None,
            "link": item.get("link")
        })
    return results

def normalize_scraper(data) -> list:
    results = []
    for item in data:
        results.append({
            "source": "Web Scraper",
            "cve": None,
            "title": item.get("title"),
            "description": item.get("description"),
            "cvss": None,
            "link": item.get("link")
        })
    return results