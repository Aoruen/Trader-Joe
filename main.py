import os
import discord
from discord.ext import commands
import random
import re
import openai
from flask import Flask
import threading

# Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is missing!")

# Set up OpenAI
openai.api_key = OPENAI_API_KEY

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Normalize helper
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# Probability command (kept intact)
@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

# AI-Powered Joe Command
@bot.command(name="joe", help="Ask Trader Joe anything!")
async def joe(ctx, *, question: str):
    prompt = f"You are Trader Joe, a witty and helpful grocery guru. Respond conversationally to the following:\n\nQ: {question}\nA:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo" for lighter usage
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        reply = response.choices[0].message["content"].strip()
        await ctx.send(reply)
    except Exception as e:
        await ctx.send("🚧 Oops! Trader Joe is out restocking. Try again later.")
        print(f"OpenAI error: {e}")

# Bot ready event
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
