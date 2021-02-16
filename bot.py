# bot.py
import stock
import os
import ftplib
import re
import random
import locale
from dotenv import load_dotenv  # used for getting environment vars
from discord.ext import commands  # functionality for bots
import discord
import matplotlib.pyplot as plt
import pymongo
from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CONNECTION_URL = os.getenv('MONGODB_CONNECTION_URL')

# connecting to MongoDB Atlas
cluster = MongoClient(CONNECTION_URL)
db = cluster["BotData"]
collection = db["BotData"]

EMBED_COLOR = 0x03f8fc
EMBED_ERR_COLOR = 0xdc143c

bot = commands.Bot(command_prefix='!')
valid_times = ['1M', '3M', '6M', 'YTD', '1Y', '2Y', '5Y']
tickers = []


# action to perform when bot is ready
@bot.event
async def on_ready():
    # set new active servers to have default values in db if they don't exist yet
    active_guilds = bot.guilds

    for guild in active_guilds:
        add_guild(guild)

    print(f'{bot.user.name} has connected to Discord!')


# !fake command
@bot.command(name='fake', help='Randomly picks an insult used on DEM BOIZ')
async def fake(ctx):
    responses = [
        'Use your head man',
        'Nah yo',
        'stop being a republican business major',
        'unlucky',
        'bot diff',
        "Cockalorum",
        "MumpSIMPus"
    ]

    response = random.choice(responses)
    await ctx.send(response)


# !stocks command
@bot.command(name='stocks', help='Posts a link that displays all the currently traded stocks')
async def stocks(ctx):
    url = "https://www.nyse.com/listings_directory/stock"
    embed = discord.Embed(description=f'List of all currently traded stocks\n{url}', color=EMBED_COLOR)
    await ctx.send(embed=embed)


# !chart command
@bot.command(name='chart', help='Charts the price history of the given stock over 1 month')
async def chart(ctx, ticker, timeframe='1M'):
    ticker = ticker.upper()

    if ticker not in tickers:
        title = 'Invalid ticker symbol entered'
        description = 'Enter a valid ticker symbol'
        embed = discord.Embed(title=title, description=description, color=EMBED_ERR_COLOR)
        await ctx.send(embed=embed)
        return

    timeframe = timeframe.upper()

    if timeframe not in valid_times:
        title = 'Invalid timeframe entered'
        description = 'Valid timeframes include:'
        embed = discord.Embed(title=title, description=description, color=EMBED_ERR_COLOR)

        for tf in valid_times:
            if tf[1] == 'M':
                embed.add_field(name=tf, value=f'{tf[0]} Month', inline=True)
            elif tf[1] == 'Y':
                embed.add_field(name=tf, value=f'{tf[0]} Year', inline=True)
            else:
                embed.add_field(name=tf, value=f'Year To Date', inline=True)

        await ctx.send(embed=embed)
        return

    data, adjusted_flag = stock.get_chart_data(ticker, timeframe)
    create_chart(ctx.guild, ticker, timeframe, data, adjusted_flag)
    embed = discord.Embed(color=EMBED_COLOR)
    file = discord.File(f'./{ticker.lower()}_chart.png', filename='image.png')
    embed.set_image(url='attachment://image.png')
    await ctx.send(file=file, embed=embed)
    os.remove(f'{ticker.lower()}_chart.png')


# !price command
@bot.command(name='price', help='Displays current price, high, low, previous close, and current volume')
async def price(ctx, ticker):
    ticker = ticker.upper()

    if ticker not in tickers:
        response = "Invalid ticker symbol entered. Make sure you typed it in correctly."
        await ctx.send(response)
        return

    price_info = stock.get_price(ticker)
    del price_info['symbol']
    del price_info['latest trading day']
    del price_info['change']

    embed = discord.Embed(title=f"__**{ticker} Daily Price History:**__", color=EMBED_COLOR,
                          timestamp=ctx.message.created_at)
    locale.setlocale(locale.LC_ALL, '')
    stat_string = ""

    for key in price_info:
        if key == 'open' or key == 'price' or key == 'high' or key == 'low' or key == 'previous close':
            stat_string += f'{key.title()}: {locale.currency(float(price_info[key]), grouping=True)}\n'
        elif key == 'change percent':
            stat_string += f'Percent Change: {price_info[key]}\n'
        elif key == 'volume':
            volume = '{:,}'.format(int(price_info[key]))
            stat_string += f'{key.title()}: {volume}\n'
        else:
            stat_string += f'{key.title()}: {price_info[key]}\n'

    embed.add_field(name='**Statistics**', value=stat_string, inline=False)
    await ctx.send(embed=embed)


# !dark command
@bot.command(name='dark', help='Changes the chart to be displayed in dark mode (default)')
async def dark(ctx):
    if guild_exists(ctx.guild):
        query = {'guild_id': ctx.guild.id}
        update = {"$set": {"theme": 0}}
        collection.update(query, update)
    else:
        add_guild(ctx.guild, theme=0)

    await ctx.send('Dark mode enabled')


# !light command
@bot.command(name='light', help='Changes the chart to be displayed in light mode')
async def light(ctx):
    if guild_exists(ctx.guild):
        query = {'guild_id': ctx.guild.id}
        update = {"$set": {"theme": 1}}
        collection.update(query, update)
    else:
        add_guild(ctx.guild, theme=1)

    await ctx.send('Light mode enabled')


# creates the chart for the given time frame
def create_chart(guild, ticker, timeframe, data, adjusted_flag=False):
    # setting default colors to dark
    bg_color = '#1F2326'
    accent_color = 'white'
    line_color = '#03F8FC'

    query = {'guild_id': guild.id}

    if guild_exists(guild):
        theme = collection.find(query).limit(1)[0]["theme"]

        if theme == 1:  # set light mode colors
            bg_color = 'white'
            accent_color = 'black'
            line_color = 'blue'
    else:
        add_guild(guild, theme=0)
    
    fig = plt.figure()
    ax = plt.gca()

    # setting the plot and background color depending on if light or dark mode is selected
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # changing the axis colors depending on if light or dark mode is seleted
    ax.spines['bottom'].set_color(accent_color)
    ax.spines['top'].set_color(accent_color)
    ax.spines['right'].set_color(accent_color)
    ax.spines['left'].set_color(accent_color)

    # changing the marking along the axes depending on if light or dark mode is selected
    ax.tick_params(axis='x', colors=accent_color)
    ax.tick_params(axis='y', colors=accent_color)

    if adjusted_flag:
        data['5. adjusted close'].plot(color=line_color)
    else:
        data['4. close'].plot(color=line_color)

    # removing the axis labels because no one needs to see that
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.title(get_chart_title(ticker, timeframe), color=accent_color)

    plt.savefig(f'{ticker.lower()}_chart.png')  # saving file locally (will be deleted in bot.py)
    plt.clf()


def get_chart_title(ticker, timeframe):
    if timeframe == '1M':
        return f'1 Month Chart for {ticker}'
    elif timeframe == '3M':
        return f'3 Month Chart for {ticker}'
    elif timeframe == '6M':
        return f'6 Month Chart for {ticker}'
    elif timeframe == 'YTD':
        return f'Year-To-Date Chart for {ticker}'
    elif timeframe == '1Y':
        return f'1 Year Chart for {ticker}'
    elif timeframe == '2Y':
        return f'2 Year Chart for {ticker}'
    else:
        return f'5 Year Chart for {ticker}'


def guild_exists(guild):
    query = {'guild_id': guild.id}

    if collection.count_documents(query, limit=1):  # no data on this guild; add a new entry
        return True
    else:
        return False


def add_guild(guild, theme=0):
    if not guild_exists(guild):
        post = {"guild_id": guild.id,
                "guild_name": guild.name,
                "theme": theme}
        collection.insert_one(post)


# checks to see if "tickers.txt" files exist before attemping to download
# if it exists, it will not spend time to redownload data and proceed to sorting tickers into a list
# if it doesn't exist it will download data and then sort tickers into a list
def download_tickers():
    if os.path.exists('tickers.txt') is False:
        # Connect to ftp.nasdaqtrader.com
        ftp = ftplib.FTP('ftp.nasdaqtrader.com', 'anonymous', 'anonymous@debian.org')

        # Download files nasdaqlisted.txt and otherlisted.txt from ftp.nasdaqtrader.com
        for file in ["nasdaqlisted.txt", "otherlisted.txt"]:
            ftp.cwd("/SymbolDirectory")
            localfile = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, localfile.write)
            localfile.close()
        ftp.quit()

        # Grep for common stock in nasdaqlisted.txt and otherlisted.txt
        for file in ["nasdaqlisted.txt", "otherlisted.txt"]:
            localfile = open(file, 'r')
            for line in localfile:
                if re.search("Common Stock", line) or re.search("Common Share", line) or \
                        re.search("common stock", line) or re.search("S&P", line) or re.search("ETF", line) or \
                        re.search("Shares", line):
                    ticker = line.split("|")[0]
                    # Append tickers to file tickers.txt
                    open("tickers.txt", "a+").write(ticker + "\n")

    file = open('tickers.txt')

    # places all the tickers in a list
    for line in file:
        tickers.append(line.rstrip('\n'))

    file.close()
    tickers.sort()


# main function to start the bot
def run():
    download_tickers()
    bot.run(TOKEN)
