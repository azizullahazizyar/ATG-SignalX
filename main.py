import os
import threading
from flask import Flask
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import aiohttp
import yfinance as yf

# -------------------------------------------------------------
# DUMMY WEB SERVER (Keeps Render Free Web Service happy)
# -------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "ScalpX AI Bot is running online!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# -------------------------------------------------------------
# AI TRADING BOT CONFIGURATION & TOP 8 SYMBOLS
# -------------------------------------------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

# Symbol Mapping for yfinance live prices
TOP_8_SYMBOLS = {
    "XAUUSD (Gold)": "GC=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "US30 (Dow Jones)": "^DJI",
    "NAS100 (Nasdaq)": "^NDX",
    "BTCUSD (Bitcoin)": "BTC-USD",
    "ETHUSD (Ethereum)": "ETH-USD",
    "USDJPY": "USDJPY=X"
}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
intents.direct_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def send_to_telegram(text: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                pass

@bot.event
async def on_ready():
    print(f"⚡ ScalpX AI Bot active as {bot.user}")
    if TARGET_CHANNEL_ID != 0 and not auto_market_scanner.is_running():
        auto_market_scanner.start()

# -------------------------------------------------------------
# 1. MANUAL CHART SCREENSHOT ANALYSIS (IMAGE VISION)
# -------------------------------------------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]):
                status_msg = await message.reply("⚡ *Scanning chart structure & scalping zones with Gemini AI Vision...*")

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                image_bytes = await resp.read()

                    symbols_list_str = ", ".join(TOP_8_SYMBOLS.keys())
                    prompt = (
                        f"You are a professional high-frequency scalper and market structure expert. "
                        f"Primary focus assets are: {symbols_list_str}. "
                        "Analyze the attached chart screenshot for micro-scalping or swing opportunities. "
                        "Identify the timeframe from the chart (1M, 3M, 5M, 15M, 1H, 4H, Daily) and return a stylish signal with emojis:\n\n"
                        "🚨 **VIP SCALP SIGNAL** 🚨\n\n"
                        "📌 **Asset / Pair:** [Detected Pair Name]\n"
                        "⏱️ **Timeframe:** [Detected Timeframe - e.g., 5M Scalp / 15M Intraday]\n"
                        "🎯 **Signal Direction:** [🟢 BUY / 🔴 SELL / 🟡 NEUTRAL]\n\n"
                        "⚡ **ENTRY & LEVELS** ⚡\n"
                        "🔹 **Entry Zone:** [Price or Range]\n"
                        "🛑 **Stop Loss (SL):** [Price]\n"
                        "🎯 **Take Profit 1 (Scalp):** [Price]\n"
                        "🚀 **Take Profit 2 (Runner):** [Price]\n"
                        "🏆 **Take Profit 3 (Final Target):** [Price]\n"
                        "⚖️ **Risk / Reward:** [R:R Ratio]\n\n"
                        "🧠 **PRO TRADING CONFLUENCE** 🧠\n"
                        "▪️ [Key reason 1: e.g., Liquidity sweep / Order block]\n"
                        "▪️ [Key reason 2: e.g., FVGs / Market structure shift]\n"
                        "▪️ [Key reason 3: e.g., Volume / Indicator confirmation]"
                    )

                    image_part = {
                        "mime_type": attachment.content_type or "image/png",
                        "data": image_bytes
                    }

                    response = model.generate_content([prompt, image_part])
                    analysis_text = response.text

                    embed = discord.Embed(
                        title="⚡ VIP SCALP SIGNAL & ANALYSIS ⚡",
                        description=analysis_text[:4000],
                        color=discord.Color.gold()
                    )
                    
                    await status_msg.edit(content=None, embed=embed)
                    await send_to_telegram(analysis_text)

                except Exception as e:
                    await status_msg.edit(content=f"❌ Error during analysis: {str(e)}")

    await bot.process_commands(message)

# -------------------------------------------------------------
# 2. AUTOMATIC LIVE MARKET SCANNER (RUNS EVERY HOUR)
# -------------------------------------------------------------
@tasks.loop(hours=1)
async def auto_market_scanner():
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        return

    market_summary = ""
    
    # Download recent 1-hour candle data for each top symbol
    for name, ticker in TOP_8_SYMBOLS.items():
        try:
            data = yf.download(ticker, period="2d", interval="1h", progress=False)
            if not data.empty:
                last_close = float(data['Close'].iloc[-1])
                prev_close = float(data['Close'].iloc[-2])
                change = ((last_close - prev_close) / prev_close) * 100
                direction = "📈" if change >= 0 else "📉"
                market_summary += f"• **{name}**: {last_close:.2f} ({direction} {change:+.2f}%)\n"
        except Exception:
            continue

    if not market_summary:
        market_summary = "Live price feeds temporarily updating..."

    auto_prompt = (
        f"You are an automated trading bot analyst. Based on the following live market prices:\n\n"
        f"{market_summary}\n"
        "Generate a brief HOURLY MARKET PULSE update highlighting market conditions for these assets. "
        "Select the 1 or 2 best-looking assets for a potential trade setup right now and provide estimated Entry, SL, and TP zones."
    )

    try:
        response = model.generate_content(auto_prompt)
        auto_signal_text = f"📊 **HOURLY LIVE MARKET SCANNER** 📊\n\n{response.text}"
        
        await channel.send(auto_signal_text)
        await send_to_telegram(auto_signal_text)
    except Exception as e:
        print(f"Error in automated scanner: {str(e)}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
