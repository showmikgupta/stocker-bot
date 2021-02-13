# bot.py
import stock
import os
import ftplib
import re
import random
from dotenv import load_dotenv  # used for getting environment vars
from discord.ext import commands  # functionality for bots
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
tickers = []


# action to perform when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# !fake command
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


# !stocks command
@bot.command(name='stocks', help='Posts a link that displays all the currently traded stocks')
async def stocks(ctx):
    response = "WIP!"
    await ctx.send(response)


# !chart command
@bot.command(name='chart', help='Charts the price history of the given stock over 1 month')
async def chart(ctx, ticker):
    ticker = ticker.upper()

    if ticker not in tickers:
        response = "Invalid ticker symbol entered. Make sure you typed it in correctly."
        await ctx.send(response)
        return

    stock.get_month_chart(ticker)
    filename = f'{ticker.lower()}_month_chart.png'
    await ctx.send(file=discord.File(filename))
    os.remove(f'{ticker.lower()}_month_chart.png')


# !price command
@bot.command(name='price', help='Displays current price, high, low, previous close, and current volume')
async def price(ctx, ticker):
    ticker = ticker.upper()
    response = f'WIP!\nFor now you can visit Yahoo Finance for up to date prices\nhttps://finance.yahoo.com/quote/{ticker}'

    if ticker not in tickers:
        response = "Invalid ticker symbol entered. Make sure you typed it in correctly."
        await ctx.send(response)
        return

    await ctx.send(response)


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
