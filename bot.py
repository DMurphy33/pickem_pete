import os
from datetime import datetime

import discord
from discord.ext import commands
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="$", intents=intents)

CSV_FILE = "bets.csv"


def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        return pd.DataFrame(
            columns=["bet_id", "user_id", "timestamp", "bet_details", "result"]
        )


def save_data(df):
    df.to_csv(CSV_FILE, index=False)


def save_bet(user_id, bet_details, bet_id, result=None):
    df = load_data()
    new_bet = pd.DataFrame(
        {
            "bet_id": [bet_id],
            "user_id": [user_id],
            "timestamp": [datetime.now().isoformat()],
            "bet_details": [bet_details],
            "result": [result],
        }
    )
    df = pd.concat([df, new_bet], ignore_index=True)
    save_data(df)


def get_user_stats(user_id):
    df = load_data()
    user_bets = df[df["user_id"] == str(user_id)]
    wins = len(user_bets[user_bets["result"] == "W"])
    losses = len(user_bets[user_bets["result"] == "L"])
    return wins, losses


def update_bet_result(bet_id, result):
    df = load_data()
    df.loc[df.bet_id == bet_id, "result"] = result
    save_data(df)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command(name="bet")
async def place_bet(ctx, *, bet_details: str):
    message = await ctx.send(
        f"{ctx.author.mention} placed a bet: {bet_details}. React with 🇼 to settle this bet as a win or with 🇱 to settle this bet as a loss."
    )
    save_bet(ctx.author.id, bet_details, message.id)
    await message.add_reaction("🇼")
    await message.add_reaction("🇱")


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if reaction.message.author == bot.user and reaction.message.content.startswith(
        f"{user.mention} placed a bet:"
    ):
        if str(reaction.emoji) == "🇼":
            update_bet_result(reaction.message.id, "W")
            await reaction.message.channel.send(
                f"{user.mention}'s bet was recorded as a win!"
            )
        elif str(reaction.emoji) == "🇱":
            update_bet_result(reaction.message.id, "L")
            await reaction.message.channel.send(
                f"{user.mention}'s bet was recorded as a loss!"
            )


@bot.command(name="stats")
async def get_stats(ctx):
    df = load_data()
    stats = df.groupby("user_id")["result"].value_counts().unstack(fill_value=0)

    response = "Betting Statistics:\n"
    for user_id, row in stats.iterrows():
        user = await bot.fetch_user(int(user_id))
        wins = row.get("W", 0)
        losses = row.get("L", 0)
        response += f"{user.name}: Wins - {wins}, Losses - {losses}\n"

    await ctx.send(response)


bot.run(TOKEN)
