import os
import discord
from discord.ext import commands
import random
import re
from openai import OpenAI
from flask import Flask
import threading

# Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # renamed to clarify

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is missing!")

# Set up OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Normalize helper
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# Prevent the bot from responding to itself
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# In-memory conversation history per user (user_id -> list of messages)
conversation_histories = {}

# Probability command
@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

# AI-Powered Joe Command with conversation history
@bot.command(name="joe", help="Ask Trader Joe anything!")
async def joe(ctx, *, question: str):
    user_id = str(ctx.author.id)

    # Initialize conversation history for the user if not exists
    if user_id not in conversation_histories:
        conversation_histories[user_id] = [
            {
                "role": "system",
                "content": "You are Trader Joe, a witty and helpful grocery guru. Please give detailed, friendly answers with examples when possible."
            }
        ]

    # Append user's message
    conversation_histories[user_id].append({"role": "user", "content": question})

    # Keep only the last 6 messages (adjust as needed)
    conversation_histories[user_id] = conversation_histories[user_id][-6:]

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=conversation_histories[user_id],
            max_tokens=400,
            temperature=0.75,
        )
        reply = response.choices[0].message.content.strip()

        # Append bot's reply to history
        conversation_histories[user_id].append({"role": "assistant", "content": reply})

        # Send plain text message (no embed)
        await ctx.send(reply)

    except Exception as e:
        await ctx.send("🚧 Oops! Trader Joe is out restocking. Try again later.")
        print(f"OpenRouter error: {e}")

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
