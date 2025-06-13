import os
import discord
from discord.ext import commands
import random
import re
import openai
from flask import Flask
import threading
import traceback

# Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is missing!")

# Set up OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Normalize helper
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# !probability command
@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

# !joe command using AI
@bot.command(name="joe", help="Ask Trader Joe anything!")
async def joe(ctx, *, question: str):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b",
            messages=[
                {"role": "system", "content": "You are Trader Joe, a witty and helpful grocery guru."},
                {"role": "user", "content": question}
            ],
            max_tokens=512,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content'].strip()
        await ctx.send(reply)
    except Exception:
        await ctx.send("⚠️ AI error — check your server logs.")
        print("AI error details:")
        print(traceback.format_exc())

# Cleaned !help command
@bot.command(name="help", help="List all commands.")
async def help_command(ctx):
    commands_list = "\n".join([
        "**!probability <sentence>** - Get a random probability for your sentence.",
        "**!joe <question>** - Ask Trader Joe a witty grocery-related question.",
        "**!help** - Show this help message."
    ])
    await ctx.send(f"📘 **Command List:**\n{commands_list}")

# Prevent message duplication
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# Bot ready event
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} — Ready on {len(bot.guilds)} servers.")

# Flask Web Server for Render/Uptime
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start web server and bot
threading.Thread(target=run_web).start()
bot.run(TOKEN)
