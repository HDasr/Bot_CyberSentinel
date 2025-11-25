import logging

# ==========================================
# 1. STRING BUILDER (Output Telegram)
# ==========================================
def format_vulnerabilities(data: list, tag="Update") -> str:
    if not data:
        return "No data available."

    msg = f"🔐 <b>{tag}</b>\n"
    msg += "Latest cybersecurity threats detected:\n\n"

    for item in data:
        cve     = item.get("cve") or "N/A"
        title   = item.get("title") or "No Title"
        cvss    = item.get("cvss")
        desc    = item.get("description") or "No description."
        link    = item.get("link")
        source  = item.get("source", "Unknown")

        msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Header Logic
        if cve != "N/A" and cve != "Unknown":
            msg += f"📌 <b>{cve}</b>"
            # Tampilkan judul hanya jika beda dengan CVE ID
            if title and title != cve and "Unknown" not in title:
                msg += f" — {title}"
            msg += "\n"
        else:
            msg += f"📢 <b>{title}</b>\n"

        # Severity / CVSS Logic
        if cvss:
            try:
                score = float(cvss)
                emoji = "🟢" if score < 4.0 else "🟡" if score < 7.0 else "🔴"
                msg += f"⚠️ CVSS: <b>{score}</b> {emoji}\n"
            except:
                # Jika CVSS berupa teks (misal: "Important")
                msg += f"⚠️ Severity: <b>{cvss}</b>\n"
        
        msg += f"📂 Source: {source}\n"
        
        # Description Limiter
        desc_str = str(desc).replace("<", "&lt;").replace(">", "&gt;") # Escape HTML tags
        if len(desc_str) > 300:
            desc_str = desc_str[:300] + "..."
        msg += f"📝 <i>{desc_str}</i>\n"

        # Link
        if link and str(link).startswith("http"):
            msg += f"🔗 <a href='{link}'>Read More</a>\n"
        
        msg += "\n"

    msg += "━━━━━━━━━━━━━━━━━━━━━━"
    return msg


# ==========================================
# 2. DATA NORMALIZERS (Sesuai JSON Anda)
# ==========================================

def standardize_data(source_name: str, raw_data) -> list:
    if not raw_data:
        return []

    if source_name == "NVD":
        return normalize_nvd(raw_data)
    elif source_name == "CIRCL":
        return normalize_circl(raw_data)
    elif source_name == "CISA":
        return normalize_cisa(raw_data)
    elif source_name == "RSS":
        return normalize_rss(raw_data)
    elif source_name == "Scraper":
        return normalize_scraper(raw_data)
    else:
        return []


def normalize_nvd(data) -> list:
    """
    Handling JSON NVD v2.0
    Path: item -> cve -> metrics -> cvssMetricV2 -> [0] -> cvssData -> baseScore
    """
    results = []
    # Data NVD dibungkus dalam list raw
    for entry in data:
        cve_obj = entry.get("cve", {})
        
        cve_id = cve_obj.get("id", "Unknown")
        
        # Description (Ambil bahasa inggris)
        descriptions = cve_obj.get("descriptions", [])
        desc_text = "No description."
        if descriptions:
            desc_text = next((d["value"] for d in descriptions if d["lang"] == "en"), descriptions[0].get("value"))

        # CVSS Logic (Cek V3.1, V3.0, lalu V2)
        metrics = cve_obj.get("metrics", {})
        cvss_score = None
        
        for ver in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if ver in metrics and metrics[ver]:
                # Struktur JSON NVD: metrics -> cvssMetricV2 -> List -> Dict -> cvssData -> baseScore
                cvss_data = metrics[ver][0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                break

        # Link
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


def normalize_circl(data) -> list:
    """
    Handling JSON CIRCL (Format RedHat Advisory berdasarkan log Anda)
    Path: item -> document -> tracking -> id
    """
    results = []
    
    for item in data:
        # Cek apakah formatnya 'document' (seperti log JSON Anda)
        doc = item.get("document", {})
        
        if doc:
            # Format RedHat / CSAF
            cve_id = doc.get("tracking", {}).get("id", "Unknown")
            title = doc.get("title", "No Title")
            
            # Severity (bukan angka, tapi teks "Important", dll)
            severity = doc.get("aggregate_severity", {}).get("text")
            
            # Description (Ambil dari notes summary)
            notes = doc.get("notes", [])
            desc = "No description."
            for note in notes:
                if note.get("category") == "summary" or note.get("category") == "general":
                    desc = note.get("text")
                    break
            
            # Link
            refs = doc.get("references", [])
            link = refs[0].get("url") if refs else None
            
            results.append({
                "source": "CIRCL",
                "cve": cve_id,
                "title": title,
                "description": desc,
                "cvss": severity, # Masukkan teks severity ke kolom CVSS
                "link": link
            })
        else:
            # Fallback ke format CIRCL standar (jika API berubah lagi)
            cve_id = item.get("id", "Unknown")
            results.append({
                "source": "CIRCL",
                "cve": cve_id,
                "title": item.get("summary", ""),
                "description": item.get("summary", ""),
                "cvss": item.get("cvss"),
                "link": f"https://cve.circl.lu/api/cve/{cve_id}"
            })

    return results


def normalize_cisa(data) -> list:
    """
    Handling JSON CISA KEV
    Structure: { 'cveID': '...', 'vulnerabilityName': '...', 'shortDescription': '...' }
    """
    results = []
    for item in data:
        results.append({
            "source": "CISA KEV",
            "cve": item.get("cveID"),
            "title": item.get("vulnerabilityName"),
            "description": item.get("shortDescription"),
            "cvss": None, # CISA KEV tidak menyediakan skor CVSS di feed ini
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