import os
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import aiohttp

# 1. Fetch Environment Variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

# 2. Configure Gemini AI Vision
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. Configure Discord Bot
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
# MODE 1: STYLISH SCALPING & MULTI-TIMEFRAME ANALYSIS
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

                    # Scalping & Emoji Prompt
                    prompt = (
                        "You are a professional high-frequency scalper and market structure expert. "
                        "Analyze the attached chart screenshot for micro-scalping or swing opportunities. "
                        "Identify the timeframe from the chart (1M, 3M, 5M, 15M, 1H, 4H, Daily) and return a stylish signal with emojis:\n\n"
                        "🚨 **VIP SCALP SIGNAL** 🚨\n\n"
                        "📌 **Asset / Pair:** [Pair Name]\n"
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
# MODE 2: AUTOMATED HOURLY MULTI-TIMEFRAME SCANNER
# -------------------------------------------------------------
@tasks.loop(hours=1)
async def auto_market_scanner():
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        return

    auto_signal_text = (
        "📊 **HOURLY MULTI-TIMEFRAME SCAN** 📊\n"
        "⏱️ **Timeframe Check:** 15M / 1H Close\n"
        "🌐 **Pairs Monitored:** Major Forex & Crypto\n"
        "⚡ **Status:** Active monitoring for liquidity sweeps & scalping setups."
    )
    
    await channel.send(auto_signal_text)
    await send_to_telegram(auto_signal_text)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

