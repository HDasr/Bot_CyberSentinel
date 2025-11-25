Tentu, ini adalah file **README.md** yang profesional dan lengkap untuk proyek **Cyber Threat Sentinel** Anda.

File ini mencakup deskripsi proyek, cara instalasi, konfigurasi, daftar fitur, dan cara penggunaan. Sangat cocok untuk dokumentasi tugas kuliah atau portofolio GitHub Anda.

Silakan simpan kode di bawah ini dengan nama `README.md`.

-----

````markdown
# 🛡️ Cyber Threat Sentinel Bot

**Cyber Threat Sentinel** adalah Bot Telegram berbasis Python yang berfungsi sebagai asisten intelijen keamanan siber (*Cyber Threat Intelligence*).

Bot ini secara otomatis mengumpulkan, menormalisasi, dan mengirimkan notifikasi mengenai kerentanan terbaru (CVE), peringatan keamanan, dan berita peretasan dari berbagai sumber terpercaya secara *real-time*.

## ✨ Fitur Utama

Bot ini mengagregasi data dari 5 sumber berbeda:

1.  **NVD (National Vulnerability Database):** Mengambil data CVE terbaru beserta skor CVSS.
2.  **CISA (Known Exploited Vulnerabilities):** Peringatan tentang celah keamanan yang sedang aktif dieksploitasi.
3.  **CIRCL (Computer Incident Response Center Luxembourg):** Laporan insiden dan advisory keamanan.
4.  **RSS Feeds:** Berita terbaru dari *The Hacker News*, *BleepingComputer*, dan *ThreatPost*.
5.  **Web Scraper:** Mengambil *headline* eksklusif langsung dari website *The Hacker News*.

### 🤖 Kemampuan Bot
* **Real-time Alerts:** Notifikasi otomatis setiap 1 jam (Scheduler).
* **On-Demand Fetch:** Perintah manual untuk menarik data kapan saja.
* **Smart Formatting:** Mengubah data JSON mentah yang rumit menjadi tampilan HTML yang rapi di Telegram.
* **Flask API:** Menyediakan endpoint HTTP sederhana `/fetch-now` untuk integrasi eksternal.

---

## 🛠️ Teknologi yang Digunakan

* **Python 3.13**
* **python-telegram-bot (v20+)** - Framework bot asinkron (`asyncio`).
* **Flask** - Web server ringan.
* **BeautifulSoup4** - Web scraping.
* **Feedparser** - Parsing RSS.
* **Requests** - HTTP Client.

---

## 🚀 Instalasi & Persiapan

Ikuti langkah-langkah ini untuk menjalankan bot di komputer lokal atau server Anda.

### 1. Clone Repository
```bash
git clone [https://github.com/username-anda/cyber-sentinel-bot.git](https://github.com/username-anda/cyber-sentinel-bot.git)
cd cyber-sentinel-bot
````

### 2\. Siapkan Environment (Opsional tapi Disarankan)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3\. Install Dependencies

Instal semua library yang dibutuhkan melalui `requirements.txt`.

> **Catatan:** Project ini menggunakan `tzlocal<3.0` untuk menjaga kompatibilitas scheduler di Windows.

```bash
pip install -r requirements.txt
```

### 4\. Konfigurasi Token

Buat folder bernama `config` dan di dalamnya buat file `config.py`:

**Struktur Folder:**

```text
/
├── config/
│   ├── __init__.py   <-- File kosong (wajib ada)
│   └── config.py     <-- Simpan token di sini
├── services/
├── main.py
...
```

**Isi file `config/config.py`:**

```python
# Token didapat dari @BotFather
TELEGRAM_TOKEN = "MASUKKAN_TOKEN_BOT_ANDA_DISINI"

# ID Chat tujuan notifikasi otomatis (Personal ID / Group ID / Channel ID)
# Didapat dari @userinfobot atau @GetIDs Bot
CHAT_ID = "123456789" 
```

-----

## ▶️ Cara Menjalankan

### 1\. Jalankan Bot

Buka terminal di root folder proyek dan jalankan:

```bash
python main.py
```

Jika berhasil, akan muncul log: `INFO:root:Bot is polling...`

### 2\. Jalankan Diagnostik (Jika Error)

Jika data tidak muncul, gunakan script diagnostik untuk mengecek koneksi ke API eksternal:

```bash
python check_services.py
```

-----

## 📱 Daftar Perintah Telegram

Kirim perintah berikut ke bot Anda:

| Perintah | Fungsi |
| :--- | :--- |
| `/start` | Mengaktifkan bot dan menampilkan menu bantuan. |
| `/now` | Mengambil 5 ancaman terbaru secara *real-time* dari semua sumber. |
| `/today` | Menampilkan ringkasan ancaman harian (Top 10). |
| `/weekly` | Menampilkan 5 ancaman dengan skor bahaya (CVSS) tertinggi minggu ini. |

-----

## 📂 Struktur Proyek

```text
Bot_Cyber_Sentinel/
├── config/                 # Konfigurasi rahasia
│   ├── __init__.py
│   └── config.py
├── services/               # Logika pengambilan data API
│   ├── cisa_service.py
│   ├── circl_service.py
│   ├── nvd_service.py
│   ├── rss_service.py
│   └── scraper_service.py
├── utils/                  # Format tampilan pesan
│   └── formatter.py
├── main.py                 # Entry point (Bot & Flask)
├── check_services.py       # Script testing/debugging
└── requirements.txt        # Daftar pustaka Python
```

-----

## ⚠️ Disclaimer

Proyek ini dibuat untuk tujuan edukasi dan penelitian akademis. Penggunaan web scraper harus mematuhi kebijakan `robots.txt` dari website target. Pengembang tidak bertanggung jawab atas penyalahgunaan informasi yang disajikan oleh bot ini.

-----

**Developed by Ayala**
Mahasiswa Informatika - UPN Veteran Jawa Timur

```
```