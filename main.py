import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from riotwatcher import LolWatcher, TftWatcher, ApiError
import json
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
REGION = os.getenv('RIOT_REGION')  # Add this line to read the region from environment variables

intents = discord.Intents.all()
client = discord.Client(intents=intents)
data_file = "data.json"
tft_watcher = TftWatcher(RIOT_API_KEY)
bot = commands.Bot(command_prefix='$', intents=intents)

def search(id, list):
    return [element['id'] for element in list if element['disc_id'] == id]

@bot.command(name='register', help="Register your summoner to Pengu")
async def register(ctx, summoner_name: str):
    data = json.loads(data_file)
    try:
        summoner = tft_watcher.summoner.by_name(REGION, summoner_name)
        await ctx.send(f'Summoner {summoner_name} has been registered.')
    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')


@bot.command(name='tft', help='Lookup a tft user with rank and last 5 games')
async def tft(ctx, summoner_name: str):
    data = json.loads(data_file)
    try:
        summoner_id = data[ctx.author.id]['id']
        summoner = tft_watcher.league.by_summoner(REGION, summoner)
        games = tft.tft_match.by_puuid(REGION, summoner['puuid'])
        await ctx.send(f'Summoner {summoner_name} has played {len(games)} TFT games.')
    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')

@bot.command(name='firstoreiff', help='Responds with "First or Eiff"')
async def firstoreiff(ctx):
    
    rand = random.randint(0,1)
    if rand == 0:
        await ctx.send('Issa :trophy: First :trophy:')
    else:
        await ctx.send('It\'s an :skull: Eiff :skull:')

    
@client.event 
async def on_ready(): print("online")

bot.run(TOKEN)