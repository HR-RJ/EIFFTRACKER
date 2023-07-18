import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from riotwatcher import LolWatcher, TftWatcher, ApiError
import json
import random
from datetime import datetime

# maybe make a local cache of the data so we don't have to make a request every time
# and maybe add logging to a file

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

def load_data():
    with open(data_file, 'r') as f:
        return json.load(f)

@bot.command(name='register', help="Register your summoner to Pengu")
async def register(ctx, *summoner_name):
    try:
        summoner = tft_watcher.summoner.by_name(REGION, "".join(summoner_name[:]))
        summoner_match = tft_watcher.match.by_id(REGION, summoner['id'])
        data = load_data()
        if str(ctx.author.id) not in data:
            json_data = {
                'id': summoner['id'], 
                'name': summoner['name'], 
                'rank': summoner_match['tier'] + ' ' + summoner_match['rank']
            }
            data[str(ctx.author.id)] = json_data
            with open(data_file, 'w') as f:
                json.dump(data, f)
            await ctx.send(f'Summoner {summoner_name} has been registered.')
        else:
            await ctx.send('You have already registered a summoner.')
    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')
            print(err)

@bot.command(name='unregister', help="Unregister your summoner from Pengu")
async def unregister(ctx):
    try:
        data = load_data
        if str(ctx.author.id) in data:
            data.pop(str(ctx.author.id))
            with open(data_file, 'w') as f:
                json.dump(data, f)
            await ctx.send('Summoner has been unregistered.')
        else:
            await ctx.send('You have not registered a summoner.')
    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')
            print(err)

@bot.command(name='tft', help='Lookup a tft user with rank and last 5 games')
async def tft(ctx, summoner_name: str):
    data = load_data()
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
    
    try:
        summoner1 = tft_watcher.summoner.by_name(REGION, summoner_name1)
        games1 = tft_watcher.tft_match.by_puuid(REGION, summoner1['puuid'])

        summoner2 = tft_watcher.summoner.by_name(REGION, summoner_name2)
        games2 = tft_watcher.tft_match.by_puuid(REGION, summoner2['puuid'])
        
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