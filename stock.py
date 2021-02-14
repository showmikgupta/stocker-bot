import os

import matplotlib
from dotenv import load_dotenv  # used for getting environment vars
from alpha_vantage.timeseries import TimeSeries  # python access to alpha vantahe api
import matplotlib.pyplot as plt

load_dotenv()
AV_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
LINE_COLOR = '#03F8FC'
BG_COLOR = '#1F2326'
ACCENT_COLOR = 'black'


# get month data for give ticker using alpha vantage api plotting daily closing prices
# using pyplot to plot pandas dataframe
def get_month_chart(ticker):
    ts = TimeSeries(key=AV_KEY, output_format='pandas')  # creating new instance of TimeSeries class
    data, meta_data = ts.get_daily(symbol=ticker)  # get daily data
    data = data[0:23]  # last months daily prices

    # by default the indexing is formatted like YYYY-MM-DD which is unnecessary
    # we will use only the month and day to index the data
    index = data.index
    closing_prices = data['4. close']
    new_index = []
    closing_reversed = []

    for date in index:
        month = date.date().month
        day = date.date().day
        date_index = f'{month}-{day}'
        new_index.append(date_index)

    for price in closing_prices:
        closing_reversed.append(price)

    new_index.reverse()
    closing_reversed.reverse()
    data.index = new_index
    data['4. close'] = closing_reversed

    fig = plt.figure()
    ax = plt.gca()

    # setting the plot and background color depending on if light or dark mode is selected
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # changing the axis colors depending on if light or dark mode is seleted
    ax.spines['bottom'].set_color(ACCENT_COLOR)
    ax.spines['top'].set_color(ACCENT_COLOR)
    ax.spines['right'].set_color(ACCENT_COLOR)
    ax.spines['left'].set_color(ACCENT_COLOR)

    # changing the marking along the axes depending on if light or dark mode is selected
    ax.tick_params(axis='x', colors=ACCENT_COLOR)
    ax.tick_params(axis='y', colors=ACCENT_COLOR)

    # plotting the data
    data['4. close'].plot(color=LINE_COLOR)

    # removing the axis labels because no one needs to see that
    ax.set_xlabel('')
    ax.set_ylabel('')

    plt.title(f'Month Chart for {ticker}', color=ACCENT_COLOR)
    plt.savefig(f'{ticker.lower()}_month_chart.png')  # saving file locally (will be deleted in bot.py)
    plt.clf()


# gets the price of the given ticker, reformats the json, and return it as a dictionary
def get_price(ticker):
    ts = TimeSeries(key=AV_KEY)
    data, meta_data = ts.get_quote_endpoint(symbol=ticker)
    # json_file = json.loads(data)
    json_dict = {}

    for key in data:
        k = key.split(' ')[1:]
        k = ' '.join(k)
        v = data[key]
        json_dict[k] = v

    return json_dict


# sets colors for dark mode
def set_dark_mode():
    global LINE_COLOR, BG_COLOR, ACCENT_COLOR
    LINE_COLOR = '#03F8FC'
    BG_COLOR = '#1F2326'
    ACCENT_COLOR = 'white'


# sets colors for light mode
def set_light_mode():
    global LINE_COLOR, BG_COLOR, ACCENT_COLOR
    LINE_COLOR = 'blue'
    BG_COLOR = 'white'
    ACCENT_COLOR = 'black'
