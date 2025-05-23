import os
import discord
from discord.ext import commands
import random
import re

# Get token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def random_probability() -> float:
    return round(random.uniform(0, 100), 2)

@bot.command(name="probability", help="Get a random probability (0-100%) for a given sentence.\nUsage: !probability <your sentence>")
async def probability(ctx, *, sentence: str):
    normalized = normalize(sentence)
    prob = random_probability()
    await ctx.send(f"🔍 Probability for: \"{normalized}\"\n🎯 Result: **{prob:.2f}%**")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} — Ready on {len(bot.guilds)} servers.")

bot.run(TOKEN)
