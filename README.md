# Stocker Discord Bot

Stocker Discord Bot is a bot that can give various statistics and charts
on any given stock that is a common stock or share. The bot is implemented
using python to handle commands and retrieving stock information from
Alpha Vantage using <a href="https://github.com/RomelTorres/alpha_vantage">this</a> 
library wrapper. There will be a web aspect of this bot that will display all
currently traded common stocks and shares, mostly likely using React.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install stocker-bot

```bash
pip install -r requirements.txt
```

## Features

The bot supports the following commands:
  * !help --- shows all the commands and their uses
  * !chart {ticker} --- displays a chart showing closing price of the given stock history over the last month
  * !price {ticker} --- displays price and other important statistics of the given stock

## To-Do

  * add the ability for users to give a time period in the !charts commands to override 1 month default
  * create website to display all stocks for user reference
  * add !movers commands that will give the top ten most daily movers****