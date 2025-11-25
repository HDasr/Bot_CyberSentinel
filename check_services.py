import logging
import json

# Import semua service
from services.nvd_service import get_latest_nvd
from services.circl_service import get_latest_circl
from services.cisa_service import get_cisa_alerts
from services.rss_service import get_rss_threats
from services.scraper_service import get_scraped_threats

# Import formatter baru
from utils.formatter import standardize_data, format_vulnerabilities

# Setup logging agar terlihat rapi
logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger("TESTER")

def test_service(service_name, fetch_function):
    print(f"\n{'='*50}")
    print(f"🛠️  SEDANG MENGECEK: {service_name}")
    print(f"{'='*50}")

    try:
        # 1. Coba Fetch Data Mentah
        print(f"[...] Menghubungi API {service_name}...")
        raw_data = fetch_function()
        
        if not raw_data:
            print(f"❌ GAGAL: {service_name} tidak mengembalikan data (Kosong/None).")
            return

        # Hitung jumlah data mentah (handling tipe data dict vs list)
        count = len(raw_data) if isinstance(raw_data, list) else len(raw_data.get('vulnerabilities', []))
        print(f"✅ SUKSES: Berhasil mengambil {count} data mentah.")

        # 2. Coba Standarisasi Data (Normalizer)
        print(f"[...] Mencoba menstandarisasi data...")
        clean_data = standardize_data(service_name, raw_data)
        
        if not clean_data:
            print(f"❌ GAGAL: Normalizer {service_name} mengembalikan list kosong.")
            return

        print(f"✅ SUKSES: Data berhasil dinormalisasi.")
        
        # 3. Tampilkan Contoh Data Bersih (Item Pertama)
        first_item = clean_data[0]
        print("\n🔎 CONTOH HASIL STANDARISASI (Item 1):")
        print(json.dumps(first_item, indent=2))

        # 4. Cek Kelengkapan Field Penting
        required_keys = ["title", "description", "link", "source"]
        missing = [key for key in required_keys if not first_item.get(key)]
        
        if missing:
            print(f"\n⚠️ WARNING: Field berikut kosong/None: {missing}")
        else:
            print("\n✨ SEMPURNA: Semua field penting terisi.")

        # 5. Cek Output HTML Telegram
        print("\n📱 PREVIEW OUTPUT TELEGRAM:")
        html_output = format_vulnerabilities([first_item], tag="Test Mode")
        print("-" * 20)
        print(html_output)
        print("-" * 20)

    except Exception as e:
        print(f"❌ ERROR CRITICAL pada {service_name}: {e}")

if __name__ == "__main__":
    # Daftar service yang akan dicek
    services = [
        ("NVD", get_latest_nvd),
        ("CIRCL", get_latest_circl),
        ("CISA", get_cisa_alerts),
        ("RSS", get_rss_threats),
        ("Scraper", get_scraped_threats),
    ]

    print("🚀 MEMULAI PENGECEKAN SEMUA SERVICE...")
    
    for name, func in services:
        test_service(name, func)
    
    print("\n🏁 PENGECEKAN SELESAI.")