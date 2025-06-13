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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # renamed to clarify

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
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # Disable default help

# Normalize helper
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# Probability command
@bot.command(name="probability", help="Returns a random probability (0–100%) for the given sentence.")
async def probability(ctx, *, sentence: str):
    norm = normalize(sentence)
    result = round(random.uniform(0, 100), 2)
    await ctx.send(f"🔍 Probability for: \"{norm}\"\n🎯 Result: **{result:.2f}%**")

# AI-Powered Joe Command using OpenRouter with your deepseek model
@bot.command(name="joe", help="Ask Trader Joe anything!")
async def joe(ctx, *, question: str):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b",
            messages=[
                {"role": "system", "content": "You are Trader Joe, a witty and helpful grocery guru."},
                {"role": "user", "content": question}
            ],
            max_tokens=4096,  # max tokens set high, as allowed by the model
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content'].strip()
        await ctx.send(reply)
    except Exception as e:
        await ctx.send("🚧 Oops! Trader Joe is out restocking. Try again later.")
        print(f"OpenRouter error: {e}")

# Plain text help command (clean and formatted)
@bot.command(name="help", help="Shows this help message.")
async def help_command(ctx):
    help_lines = ["**Help - List of Commands**", "Use `!<command>` to run a command.\n"]
    for command in bot.commands:
        if command.hidden or not command.help:
            continue
        help_lines.append(f"**!{command.name}** - {command.help}")
    help_message = "\n".join(help_lines)
    # Discord message limit is ~2000 chars, so split if needed
    for chunk in [help_message[i:i+1900] for i in range(0, len(help_message), 1900)]:
        await ctx.send(chunk)

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
