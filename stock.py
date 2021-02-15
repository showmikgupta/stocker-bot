import os
import datetime
import dateutil.relativedelta
from dotenv import load_dotenv  # used for getting environment vars
from alpha_vantage.timeseries import TimeSeries  # python access to alpha vantage api
import matplotlib.pyplot as plt

load_dotenv()
AV_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
LINE_COLOR = '#03F8FC'
BG_COLOR = '#1F2326'
ACCENT_COLOR = 'black'


# get data for give ticker for give timeframe using alpha vantage api plotting closing prices
# using pyplot to plot pandas dataframe
def get_chart(ticker, timeframe):
    ts = TimeSeries(key=AV_KEY, output_format='pandas')  # creating new instance of TimeSeries class
    current_time = datetime.datetime.now()
    data, meta_data = [], []

    # get only the relevant data for the given timeframe
    if timeframe == '1M':
        data, meta_data = get_month_data(ticker, ts, current_time)
    elif timeframe == '3M':
        data, meta_data = get_three_month_data(ticker, ts, current_time)
    elif timeframe == '6M':
        data, meta_data = get_six_month_data(ticker, ts, current_time)
    elif timeframe == 'YTD':
        data, meta_data = get_ytd_data(ticker, ts, current_time)
    elif timeframe == '1Y':
        data, meta_data = get_year_data(ticker, ts, current_time)
    elif timeframe == '2Y':
        data, meta_data = get_two_year_data(ticker, ts, current_time)
    else:
        data, meta_data = get_five_year_data(ticker, ts, current_time)

    index = data.index
    closing_prices = data['4. close']
    new_index = []
    closing_reversed = []

    # by default the indexing is formatted like YYYY-MM-DD which is unnecessary
    # we will change the date format to index depending on the timeframe
    if timeframe == '1M' or timeframe == '3M' or timeframe == '6M' or timeframe == 'YTD':
        for date in index:
            month = date.date().month
            day = date.date().day
            date_index = f'{month}-{day}'
            new_index.append(date_index)
    else:
        for date in index:
            month = date.date().month
            year = date.date().year
            date_index = f'{month}-{year}'
            new_index.append(date_index)

    for price in closing_prices:
        closing_reversed.append(price)

    # applying reformatted indices and reversed closing prices
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
    plt.title(get_chart_title(ticker, timeframe), color=ACCENT_COLOR)

    plt.savefig(f'{ticker.lower()}_chart.png')  # saving file locally (will be deleted in bot.py)
    plt.clf()


# returns a slice of the original dataset relevant for the past month
def get_month_data(ticker, ts, current_time):
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(months=-1))

    return data, meta_data


# returns a slice of the original dataset relevant for the past three months
def get_three_month_data(ticker, ts, current_time):
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(months=-3))

    return data, meta_data


# returns a slice of the original dataset relevant for the past six months
def get_six_month_data(ticker, ts, current_time):
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(months=-6))

    return data, meta_data


# returns a slice of the original dataset relevant for the year-to-date
def get_ytd_data(ticker, ts, current_time):
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')
    data = get_shortened_data(data, datetime.datetime(current_time.year, 1, 1))

    return data, meta_data


# returns a slice of the original dataset relevant for the past year
def get_year_data(ticker, ts, current_time):
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(years=-1))

    return data, meta_data


# returns a slice of the original dataset relevant for the past two years
def get_two_year_data(ticker, ts, current_time):
    data, meta_data = ts.get_weekly(symbol=ticker)
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(years=-2))

    return data, meta_data


# returns a slice of the original dataset relevant for the past 5 years
def get_five_year_data(ticker, ts, current_time):
    data, meta_data = ts.get_weekly(symbol=ticker)
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(years=-5))

    return data, meta_data


def get_shortened_data(data, limit):
    counter = 0
    dates = data.index

    for date in dates:
        if date.date() >= limit.date():
            counter += 1
        elif date.date().year == limit.date().year and date.date().month == limit.date().month and \
                date.date().day == limit.date().day:
            counter += 1
        else:
            break

    return data[:counter]


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
