import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import Button, View
from riotwatcher import TftWatcher, ApiError
import json
import random
from datetime import datetime
import arrow
import re


# maybe make a local cache of the data so we don't have to make a request every time
# and maybe add logging to a file
# help command

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
REGION = os.getenv('RIOT_REGION')  # Add this line to read the region from environment variables


intents = discord.Intents.all()
client = discord.Client(intents=intents)
data_file = "data.json"
tft_watcher = TftWatcher(RIOT_API_KEY)
bot = commands.Bot(command_prefix='$', intents=intents)
class PaginationView(View):
    def __init__(self, pages):
        super().__init__(timeout=None)  # disable the View timeout
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.blurple)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
@client.event 
async def on_ready(): print("online")

def search(id, list):
    return [element['id'] for element in list if element['disc_id'] == id]

def load_data():
    with open(data_file, 'r') as f:
        return json.load(f)

def to_datetime(unix):
    amsterdam_tz = 'Europe/Amsterdam'
    date = 1689699290915
    return arrow.get(unix).to(amsterdam_tz).datetime.strftime('%Y/%m/%d %H:%M:%S')


def get_matches(puuid):
    # TODO: get little legend icons, store little legend species, 
    # placement, time, augments, health at end of game?,
    match_list = tft_watcher.match.by_puuid("EUROPE", puuid, count=5, start=0)
    return match_list

def get_match(match_id, puuid):
    match = tft_watcher.match.by_id("EUROPE", match_id)
    date = to_datetime(match['info']['game_datetime']) # TODO change unix to datetime done :)
    summoner = match['info']['participants'][match['metadata']['participants'].index(puuid)]
    placement = summoner['placement']
    players = [tft_watcher.summoner.by_puuid(REGION, id)['name'] for id in match['metadata']['participants']]
    augment = summoner['augments']
    return {'date': date, 'placement': placement, 'augments': augment, 'players': players}


@bot.command(name='register', help="Register your summoner to Pengu")
async def register(ctx, *summoner_name):
    try:
        summoner = tft_watcher.summoner.by_name(REGION, " ".join(summoner_name[:]))
        summoner_match_list = get_matches(summoner['puuid'])
        summoner_league = tft_watcher.league.by_summoner(REGION, summoner['id'])
        print(summoner_league)
        data = load_data()
        if str(ctx.author.id) not in data['users']:
            json_data = {
                'id': summoner['id'], 
                'name': summoner['name'], 
                'rank': summoner_league[0]['tier'][0]+summoner_league[0]['tier'][1:].lower() + ' ' 
                    + summoner_league[0]['rank']+" "+ str(summoner_league[0]["leaguePoints"])+" LP",
                'puuid': summoner['puuid'],
                'last_matches': [get_match(match, summoner['puuid']) for match in summoner_match_list]
            }
            data['users'][str(ctx.author.id)] = json_data
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4, separators=(',',': '))
            await ctx.send("Summoner **"+ summoner['name'] +"** has been registered.") #TODO link name to lolchess
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
        data = load_data()
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

@bot.command(name='tftme', help='Lookup yourself with rank and last 5 games')
async def tftme(ctx):
    data = load_data()
    # try:
    pages = []

    summoner = data['users'][str(ctx.author.id)]

    for item in summoner['last_matches']:
        embed = discord.Embed(title=summoner['name'], description="**Rank:** "+summoner['rank'], color=0x0089ff)
        message = arrow.get(item['date']).humanize()+'\n'
        for i in range(0,7,2):
            message = message + item['players'][i]+'\t'+item['players'][i+1] +'\n'
        message = message + "\nTraits:\n"
        for id, aug in enumerate(item['augments']):
            message = message+str(id+1)+" - "
            augment = aug.split('_')[-1]
            split_by_capital = re.findall('[A-Z][^A-Z]*', augment)
            message = message +" ".join(split_by_capital)
            message = message +'\n'
        embed.add_field(name="\#"+str(item["placement"]), value=message, inline=False)
        pages.append(embed)

    view=PaginationView(pages)
    await ctx.send(embed=pages[0], view=view)


@bot.command(name='tft', help='Lookup a tft user with rank and last 5 games') #no name only disc id check from user
async def tft(ctx, summoner_name: str):
    data = load_data()
    try:
        summoner_id = data['users'][ctx.author.id]['id']
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
        games1 = tft_watcher.summoner.by_puuid(REGION, summoner1['puuid'])

        summoner2 = tft_watcher.summoner.by_name(REGION, summoner_name2)
        games2 = tft_watcher.summoner.by_puuid(REGION, summoner2['puuid'])
        
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


bot.run(TOKEN)