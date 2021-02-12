# bot.py
import os
import random
from dotenv import load_dotenv #used for getting environment vars
from discord.ext import commands #functionality for bots

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

#action to perform when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#!fake command
@bot.command(name='fake', help='Randomly picks an insult used on DEM BOIZ')
async def fake(ctx):
	responses = [
		'Use your head man',
		'Nah yo',
		'stop being a republican business major',
		'unlucky',
		'bot diff'
	]
	
	response = random.choice(responses)
	await ctx.send(response)

#!stocks
@bot.command(name='stocks', help='Posts a link that displays all the currently traded stocks')
async def stocks(ctx):
	response = "WIP!"
	await ctx.send(response)

bot.run(TOKEN)