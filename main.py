import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from riotwatcher import LolWatcher, TftWatcher, ApiError
import json
import random
from datetime import datetime

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

@bot.command(name='compare', help='Compares the average placements of two summoners')
async def compare(ctx, summoner_name1: str, summoner_name2: str):
    lol_watcher = LolWatcher(RIOT_API_KEY)
    my_region = REGION
    
    try:
        summoner1 = lol_watcher.summoner.by_name(my_region, summoner_name1)
        games1 = lol_watcher.tft_match.by_puuid(my_region, summoner1['puuid'])

        summoner2 = lol_watcher.summoner.by_name(my_region, summoner_name2)
        games2 = lol_watcher.tft_match.by_puuid(my_region, summoner2['puuid'])
        
        placement_data1 = process_games(games1)
        placement_data2 = process_games(games2)

        average_placement1 = sum(placement_data1.values()) / len(placement_data1)
        average_placement2 = sum(placement_data2.values()) / len(placement_data2)
        
        # Convert averages to emoji string
        emoji1 = '🟦'
        emoji2 = '🟧'
        bar = emoji1 * int(average_placement1) + emoji2 * int(average_placement2)
        result = f'{summoner_name1}: {emoji1 * int(average_placement1)}\n{summoner_name2}: {emoji2 * int(average_placement2)}\n{bar}'
        
        await ctx.send(result)

    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')
    
def process_games(games):
    placements = {}
    for game in games:
        date = datetime.fromtimestamp(game['info']['game_datetime'] / 1000).date()
        if date not in placements:
            placements[date] = []
        placements[date].append(game['info']['participants'][0]['placement'])
    # calculate average
    for date, placement_list in placements.items():
        placements[date] = sum(placement_list) / len(placement_list)
    return placements

@client.event 
async def on_ready(): print("online")

bot.run(TOKEN)