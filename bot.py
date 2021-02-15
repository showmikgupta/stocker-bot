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

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
valid_times = ['1M', '3M', '6M', 'YTD', '1Y', '2Y', '5Y']
tickers = []


# action to perform when bot is ready
@bot.event
async def on_ready():
    stock.set_dark_mode()
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
    response = "https://www.nyse.com/listings_directory/stock"
    await ctx.send(f'List of all currently traded stocks\n{response}')


# !chart command
@bot.command(name='chart', help='Charts the price history of the given stock over 1 month')
async def chart(ctx, ticker, timeframe='1M'):
    ticker = ticker.upper()

    if ticker not in tickers:
        title = 'Invalid ticker symbol entered'
        description = 'Enter a valid ticker symbol'
        embed = discord.Embed(title=title, description=description, color=0xdc143c)
        await ctx.send(embed=embed)
        return

    timeframe = timeframe.upper()

    if timeframe not in valid_times:
        title = 'Invalid timeframe entered'
        description = 'Valid timeframes include:'
        embed = discord.Embed(title=title, description=description, color=0xdc143c)

        for tf in valid_times:
            if tf[1] == 'M':
                embed.add_field(name=tf, value=f'{tf[0]} Month', inline=True)
            elif tf[1] == 'Y':
                embed.add_field(name=tf, value=f'{tf[0]} Year', inline=True)
            else:
                embed.add_field(name=tf, value=f'Year To Date', inline=True)

        await ctx.send(embed=embed)
        return

    stock.get_chart(ticker, timeframe)
    embed = discord.Embed(color=0x03f8fc)
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

    embed = discord.Embed(title=f"__**{ticker} Daily Price History:**__", color=0x03f8fc,
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
    stock.set_dark_mode()
    await ctx.send('Dark mode enabled')


# !light command
@bot.command(name='light', help='Changes the chart to be displayed in light mode')
async def light(ctx):
    stock.set_light_mode()
    await ctx.send('Light mode enabled')


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
                if re.search("Common Stock", line) or re.search("Common Share", line):
                    ticker = line.split("|")[0]
                    # Append tickers to file tickers.txt
                    open("tickers.txt", "a+").write(ticker + "\n")

    file = open('tickers.txt')

    # places all the tickers in a list
    for line in file:
        tickers.append(line.rstrip('\n'))

    file.close()
    tickers.sort()


download_tickers()
bot.run(TOKEN)
