import asyncio
import logging
import threading
from flask import Flask, jsonify
import os

from config import TELEGRAM_TOKEN, CHAT_ID

from telegram import BotCommand
from telegram.ext import Application, CommandHandler

from services.nvd_service import get_latest_nvd
from services.cisa_service import get_cisa_alerts
from services.rss_service import get_rss_threats
from services.scraper_service import get_scraped_threats
from utils.formatter import format_vulnerabilities, standardize_data


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)


def fetch_aggregated_data():
    aggregated = {
        "NVD": [],
        "CISA": [],
        "NEWS": []
    }

    # Fetching NVD
    try:
        raw_nvd = get_latest_nvd()
        if raw_nvd:
            clean_nvd = standardize_data("NVD", raw_nvd)
            aggregated["NVD"] = clean_nvd[:20]
    except Exception as e:
        log.error(f"NVD Error: {e}")

    # Fetching CISA
    try:
        raw_cisa = get_cisa_alerts()
        if raw_cisa:
            clean_cisa = standardize_data("CISA", raw_cisa)
            aggregated["CISA"] = clean_cisa[:20]
    except Exception as e:
        log.error(f"CISA Error: {e}")

    # Fetching Scraper
    try:
        raw_news = get_scraped_threats() 
        source_name = "Scraper"
        
        if not raw_news:
            raw_news = get_rss_threats()
            source_name = "RSS"

        if raw_news:
            clean_news = standardize_data(source_name, raw_news)
            aggregated["NEWS"] = clean_news[:20]
    except Exception as e:
        log.error(f"News Error: {e}")

    return aggregated


def merge_and_prioritize(data_dict, limit):
    final_list = []
    
    quota = int(limit / 3) 
    
    cisa_data = data_dict.get("CISA", [])
    final_list.extend(cisa_data[:quota])
    
    nvd_data = data_dict.get("NVD", [])
    if nvd_data:
        sorted_nvd = sorted(
            nvd_data, 
            key=lambda x: float(x.get("cvss") or 0), 
            reverse=True
        )
        final_list.extend(sorted_nvd[:quota])
        
    news_data = data_dict.get("NEWS", [])
    final_list.extend(news_data[:quota])
    
    current_count = len(final_list)
    if current_count < limit:
        needed = limit - current_count
        
        if len(cisa_data) > quota:
            final_list.extend(cisa_data[quota : quota + needed])
            
        current_count = len(final_list)
        needed = limit - current_count
        
        if needed > 0 and len(nvd_data) > quota:
            final_list.extend(sorted_nvd[quota : quota + needed])
            
        current_count = len(final_list)
        needed = limit - current_count
        if needed > 0 and len(news_data) > quota:
            final_list.extend(news_data[quota : quota + needed])

    return final_list[:limit]

async def cmd_start(update, context):
    welcome_text = (
        "🔐 <b>Cyber Threat Sentinel Activated</b>\n\n"
        "Your real-time cybersecurity assistant is now online.\n"
        "Use the commands below to retrieve the latest threat intelligence:\n\n"
        "📌 <b>Available Commands</b>\n"
        "• /today — Get today’s summary (Top 15 Most Important)\n"
        "• /weekly — Weekly highlights (Top 10 High Risk)\n"
        "• /now — Quick update (Top 5 Latest)\n\n"
        "🛡️ The bot also sends automatic hourly updates to keep you informed."
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")


async def cmd_today(update, context):
    await update.message.reply_text("🔄 Fetching top 15 threats for today...", parse_mode="HTML")
    
    data_dict = fetch_aggregated_data()
    top_15 = merge_and_prioritize(data_dict, limit=15)

    if not top_15:
        await update.message.reply_text("No data available at the moment.")
        return

    msg_list = format_vulnerabilities(top_15, "📅 Today's Intelligence (Top 15)")
    
    for part in msg_list:
        await update.message.reply_text(part, parse_mode="HTML")


async def cmd_weekly(update, context):
    await update.message.reply_text("🔄 Fetching top 10 weekly highlights...", parse_mode="HTML")
    
    data_dict = fetch_aggregated_data()
    top_10 = merge_and_prioritize(data_dict, limit=10)

    if not top_10:
        await update.message.reply_text("No data available.")
        return

    msg_list = format_vulnerabilities(top_10, "🗓️ Weekly Highlights (Top 10)")
    
    for part in msg_list:
        await update.message.reply_text(part, parse_mode="HTML")


async def cmd_now(update, context):
    data_dict = fetch_aggregated_data()
    top_5 = merge_and_prioritize(data_dict, limit=5)

    if not top_5:
        await update.message.reply_text("No data available.")
        return

    msg_list = format_vulnerabilities(top_5, "⚡ Real-time Threats (Top 5)")
    
    for part in msg_list:
        await update.message.reply_text(part, parse_mode="HTML")


async def scheduler(app_obj):
    await asyncio.sleep(10) 
    
    while True:
        log.info("🕒 Scheduler Running: Fetching data Aggregator...")
        
        data = fetch_aggregated_data()
        
        if data["NEWS"]:
            msg_list = format_vulnerabilities(data["NEWS"][:5], "📰 Report Cyber News")
            await send_to_group(app_obj, msg_list)

        if data["CISA"]:
            msg_list = format_vulnerabilities(data["CISA"][:5], "🚨 CISA Known Exploited")
            await send_to_group(app_obj, msg_list)
            
        if data["NVD"]:
            sorted_nvd = sorted(data["NVD"], key=lambda x: float(x.get("cvss") or 0), reverse=True)
            msg_list = format_vulnerabilities(sorted_nvd[:5], "🛠️ NVD High Risk Update")
            await send_to_group(app_obj, msg_list)

        log.info("✅ Report sent. Next report in 6 hours.")
        await asyncio.sleep(21600) # 6 Hours

async def send_to_group(app_obj, msg_input):
    if CHAT_ID:
        try:
            if isinstance(msg_input, list):
                for part in msg_input:
                    await app_obj.bot.send_message(chat_id=CHAT_ID, text=part, parse_mode="HTML")
                    await asyncio.sleep(1)
            else:
                await app_obj.bot.send_message(chat_id=CHAT_ID, text=msg_input, parse_mode="HTML")
                
        except Exception as e:
            log.error(f"Gagal kirim ke grup: {e}")


async def post_init(app_obj):
    app_obj.create_task(scheduler(app_obj))
    
    commands = [
        BotCommand("start", "Activate the bot"),
        BotCommand("today", "Top 15 Threats"),
        BotCommand("weekly", "Top 10 Highlights"),
        BotCommand("now", "Top 5 Latest"),
    ]
    await app_obj.bot.set_my_commands(commands)
    log.info("Bot Ready.")


@app.route("/fetch-now")
def fetch_now_api():
    data = fetch_aggregated_data()
    prioritized = merge_and_prioritize(data, 100)
    return jsonify({
        "total_items": len(prioritized),
        "data": prioritized
    })

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def main():
    threading.Thread(target=run_flask, daemon=True).start()

    bot_app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    bot_app.add_handler(CommandHandler("start", cmd_start))
    bot_app.add_handler(CommandHandler("today", cmd_today))
    bot_app.add_handler(CommandHandler("weekly", cmd_weekly))
    bot_app.add_handler(CommandHandler("now", cmd_now))

    bot_app.run_polling()


if __name__ == "__main__":
    main()