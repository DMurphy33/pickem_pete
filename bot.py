import os

import discord
import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="$")

if not os.path.exists(bets_path := "bets.csv"):
    bets = pd.DataFrame(columns=["bet_id", "user_id", "bet", "result"])
else:
    bets = pd.read_csv(bets_path)


async def on_message(message):
    if message.channel.name != "general":
        return
    await bot.process_commands(message)


bot.on_message = on_message


@bot.command(name="bet", help="Enter the pick you wish to make. Example: $bet PHI -3")
async def place_bet(ctx, *, bet):
    bet_row = [ctx.message.id, ctx.message.author.id, bet, None]
    global bets
    idx = len(bets)
    bets.loc[idx] = bet_row
    bets.to_csv(bets_path, index=False)
    await ctx.reply(
        f"{ctx.message.author.display_name} placed bet {bet}. React to this message with :regional_indicator_w: to update this bet as a win or :regional_indicator_l: to update this bet as a loss."
    )


def settle_bet(bet, result):
    pass


@bot.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    if channel.name == "general" and reaction.message.author.name == "Pick'em Pete":
        if reaction.emoji == "🇼":
            await channel.send("WWWWWWW")
        elif reaction.emoji == "🇱":
            await channel.send("LLLLLLL")
        else:
            return


bot.run(TOKEN)
