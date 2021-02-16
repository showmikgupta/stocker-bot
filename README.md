# Stocker Discord Bot

Stocker Discord Bot is a bot that can give various statistics and charts
on any given stock. The bot is implemented using python to handle commands and retrieving stock information from
Alpha Vantage using <a href="https://github.com/RomelTorres/alpha_vantage">this</a> 
library wrapper.

## Installation

This is only for stocker-bot developers to use to work on and run the bot locally on their machine.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install stocker-bot

```bash
pip install -r requirements.txt
```

Make sure to ask me for the .env files so you can get the DISCORD_TOKEN and ALPHAVANTAGE_API_KEY

## Commands

The bot supports the following commands:
  * **!help** --- shows all the commands and description
  * **!chart** {ticker} {timeframe=optional} --- displays a chart showing closing price of the given stock history over the given
    timeframe. Timeframes include 1M (default), 3M, 6M, YTD, 1Y, 2Y, and 5Y.
  * **!price** {ticker} --- displays the current, high, low, open, and previous closing prices along with the percent change
    and the volume.
  * **!stocks** --- Sends a link to the New York Stock Exchange directory with all the currently traded securities.  
  * **!dark** --- Enables dark mode for charts (default).
  * **!light** --- Enables light mode for charts.

There are more commands that are going to be added for technical indicators and top daily movers.