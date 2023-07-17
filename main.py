import os
from dotenv import load_dotenv
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
REGION = os.getenv('RIOT_REGION')  # Add this line to read the region from environment variables

bot = commands.Bot(command_prefix='!')

@bot.command(name='tft', help='Responds with user\'s TFT games')
async def tft(ctx, summoner_name: str):
    lol_watcher = LolWatcher(RIOT_API_KEY)
    my_region = REGION  # Change this line to use the region from environment variables
    
    try:
        summoner = lol_watcher.summoner.by_name(my_region, summoner_name)
        games = lol_watcher.tft_match.by_puuid(my_region, summoner['puuid'])
        await ctx.send(f'Summoner {summoner_name} has played {len(games)} TFT games.')
    except ApiError as err:
        if err.response.status_code == 429:
            await ctx.send('We have hit the rate limit. Please try again later.')
        else:
            await ctx.send('There was an error getting the data.')

bot.run(TOKEN)
