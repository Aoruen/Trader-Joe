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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is missing!")

# Set up OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Remove default help command
bot.remove_command("help")

# Normalize helper
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# In-memory conversation history per user
conversation_histories = {}

# Probability command
@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

# General-purpose AI command (formerly "Trader Joe")
@bot.command(name="joe", help="Ask anything – AI will respond intelligently.")
async def joe(ctx, *, question: str):
    user_id = str(ctx.author.id)

    # Initialize conversation history for user if missing
    if user_id not in conversation_histories:
        conversation_histories[user_id] = [
            {
                "role": "system",
                "content": "You are a helpful and knowledgeable assistant who can answer any question clearly and usefully."
            }
        ]

    # Append user message to history
    conversation_histories[user_id].append({"role": "user", "content": question})

    # Keep last 6 messages max
    conversation_histories[user_id] = conversation_histories[user_id][-6:]

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=conversation_histories[user_id],
            max_tokens=5000,
            temperature=0.7
        )
        reply = completion.choices[0].message.content.strip()

        # Append bot reply to history
        conversation_histories[user_id].append({"role": "assistant", "content": reply})

        await ctx.send(reply)
    except Exception as e:
        await ctx.send("⚠️ Mini Aoruen Crashed The Car. Try again shortly.")
        print(f"[AI Error] {e}")

# Custom help command
@bot.command(name="help", help="List all available commands.")
async def help_command(ctx):
    help_text = (
        "🛠 **Available Commands:**\n"
        "**!probability <sentence>** – Get a random probability for your sentence.\n"
        "**!joe <question>** – Ask any question and get an intelligent AI response.\n"
        "**!help** – Show this help message."
    )
    await ctx.send(help_text)

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
