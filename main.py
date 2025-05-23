import os
import discord
from discord.ext import commands
import random
import re
from flask import Flask
import threading

# Discord Bot Setup
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} — Ready on {len(bot.guilds)} servers.")

# Minimal Flask Web Server to satisfy Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start web server in background thread
threading.Thread(target=run_web).start()

# Start the bot
bot.run(TOKEN)
