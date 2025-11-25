import asyncio
import logging
import threading
from flask import Flask, jsonify

from config import TELEGRAM_TOKEN, CHAT_ID

from telegram import BotCommand
from telegram.ext import Application, CommandHandler

from services.nvd_service import get_latest_nvd
from services.circl_service import get_latest_circl
from services.cisa_service import get_cisa_alerts
from services.rss_service import get_rss_threats
from services.scraper_service import get_scraped_threats
from utils.formatter import format_vulnerabilities, standardize_data


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)


# -------------------------------------------------------------
# FETCH ALL SOURCES (SYNC)
# -------------------------------------------------------------
def fetch_all_sources_sync():
    sources = [
        ("NVD", get_latest_nvd),
        ("CIRCL", get_latest_circl),
        ("CISA", get_cisa_alerts),
        ("RSS", get_rss_threats),
        ("Scraper", get_scraped_threats),
    ]

    for name, fn in sources:
        try:
            data = fn()
            if data:
                return name, data
        except Exception as e:
            log.error(f"{name} error: {e}")

    return None, []


# -------------------------------------------------------------
# TELEGRAM COMMANDS
# -------------------------------------------------------------
async def cmd_start(update, context):
    welcome_text = (
        "🔐 <b>Cyber Threat Sentinel Activated</b>\n\n"
        "Your real-time cybersecurity assistant is now online.\n"
        "Use the commands below to retrieve the latest threat intelligence:\n\n"
        "📌 <b>Available Commands</b>\n"
        "• /today — Get today’s vulnerability summary (up to 10 CVEs)\n"
        "• /weekly — Top 5 highest-risk CVEs this week\n"
        "• /now — Fetch the most recent threats in real-time\n\n"
        "🛡️ The bot also sends automatic hourly updates to keep you informed.\n\n"
        "If you need additional features, feel free to request them anytime."
    )

    await update.message.reply_text(welcome_text, parse_mode="HTML")



async def cmd_today(update, context):
    src, raw_data = fetch_all_sources_sync()
    if not raw_data:
        await update.message.reply_text("No data available.")
        return

    # 1. Standarisasi Data dulu!
    clean_data = standardize_data(src, raw_data)

    # 2. Baru di-slice dan diformat
    msg = format_vulnerabilities(clean_data[:10], f"Daily Threat Summary ({src})")
    await update.message.reply_text(msg, parse_mode="HTML")


async def cmd_weekly(update, context):
    src, raw_data = fetch_all_sources_sync()
    if not raw_data:
        await update.message.reply_text("No data available.")
        return

    # 1. Standarisasi Data
    clean_data = standardize_data(src, raw_data)

    # 2. Sorting Data (Sekarang aman karena kuncinya sudah pasti 'cvss')
    # Mengubah None menjadi 0 agar tidak error saat sort
    sorted_data = sorted(
        clean_data, 
        key=lambda x: float(x.get("cvss") or 0), 
        reverse=True
    )

    msg = format_vulnerabilities(sorted_data[:5], f"Top 5 Weekly Threats ({src})")
    await update.message.reply_text(msg, parse_mode="HTML")


async def cmd_now(update, context):
    src, raw_data = fetch_all_sources_sync()
    if not raw_data:
        await update.message.reply_text("No data available.")
        return

    clean_data = standardize_data(src, raw_data)
    msg = format_vulnerabilities(clean_data[:5], f"Realtime Update ({src})")
    await update.message.reply_text(msg, parse_mode="HTML")


# -------------------------------------------------------------
# BACKGROUND SCHEDULER (runs every hour)
# -------------------------------------------------------------
async def scheduler(app_obj):
    await asyncio.sleep(5)
    while True:
        log.info("Scheduler running...")
        src, raw_data = fetch_all_sources_sync() # Ambil data mentah

        if raw_data:
            # Standarisasi sebelum kirim
            clean_data = standardize_data(src, raw_data) 
            
            msg = format_vulnerabilities(clean_data[:5], f"Auto Update ({src})")
            try:
                # Pastikan CHAT_ID ada
                if CHAT_ID: 
                    await app_obj.bot.send_message(
                        chat_id=CHAT_ID,
                        text=msg,
                        parse_mode="HTML"
                    )
                else:
                    log.warning("CHAT_ID not set, skipping message.")
            except Exception as e:
                log.error(f"Scheduler send error: {e}")

        await asyncio.sleep(3600)


# -------------------------------------------------------------
# POST INIT (important)
# -------------------------------------------------------------
async def post_init(app_obj):
    """
    This function is executed AFTER the application event loop is alive.
    Perfect place to start background tasks and set bot commands.
    """
    # Create background hourly scheduler
    app_obj.create_task(scheduler(app_obj))
    log.info("Background scheduler started.")

    # Register bot command menu
    commands = [
        BotCommand("start", "Activate the bot"),
        BotCommand("today", "Get today's threat summary"),
        BotCommand("weekly", "Top 5 highest CVSS this week"),
        BotCommand("now", "Fetch latest threats right now"),
    ]
    await app_obj.bot.set_my_commands(commands)
    log.info("Bot command menu registered.")


# -------------------------------------------------------------
# FLASK SERVER
# -------------------------------------------------------------
@app.route("/fetch-now")
def fetch_now():
    src, raw_data = fetch_all_sources_sync()
    clean_data = standardize_data(src, raw_data) # Standarisasi juga buat API
    return jsonify({
        "source": src,
        "total": len(clean_data),
        "sample": clean_data[:5]
    })

def run_flask():
    app.run(host="0.0.0.0", port=5000)


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
def main():
    # Run Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Build bot
    bot_app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Commands
    bot_app.add_handler(CommandHandler("start", cmd_start))
    bot_app.add_handler(CommandHandler("today", cmd_today))
    bot_app.add_handler(CommandHandler("weekly", cmd_weekly))
    bot_app.add_handler(CommandHandler("now", cmd_now))

    # Run bot
    bot_app.run_polling()


if __name__ == "__main__":
    main()
