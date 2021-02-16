import os
import datetime
import dateutil.relativedelta
from alpha_vantage.timeseries import TimeSeries  # python access to alpha vantage api

AV_KEY = os.getenv('ALPHAVANTAGE_API_KEY')


# get data for give ticker for give timeframe using alpha vantage api plotting closing prices
# using pyplot to plot pandas dataframe
def get_chart_data(ticker, timeframe):
    ts = TimeSeries(key=AV_KEY, output_format='pandas')  # creating new instance of TimeSeries class
    current_time = datetime.datetime.now()
    data, meta_data = [], []
    labeling_flag = False
    adjusted_flag = False  # flag to determine if adjusted prices are needed for the dataset

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
        adjusted_flag = True
    else:
        data, meta_data = get_five_year_data(ticker, ts, current_time)
        adjusted_flag = True

    index = data.index
    new_index = []
    closing_prices = []
    closing_reversed = []

    # need to get adjusted weekly data for timeframes greater than or equal to 2 years (2Y)
    if adjusted_flag:
        closing_prices = data['5. adjusted close']
    else:
        closing_prices = data['4. close']

    updated_timeframe = timeframe

    # if a stock hasn't been traded as long as the given timeframe, we need to adjust the timeframe to show in the chart
    if timeframe == '2Y' or timeframe == '5Y':
        month_delta = (current_time.date() - data.index[-1].date()).days / 30

        if month_delta < 24:
            if month_delta <= 1:
                updated_timeframe = '1M'
            elif month_delta <= 3:
                updated_timeframe = '3M'
            elif month_delta <= 6:
                updated_timeframe = '6M'
            elif month_delta <= 12:
                updated_timeframe = '1Y'
            else:
                updated_timeframe = '2Y'

    # by default the indexing is formatted like YYYY-MM-DD which is unnecessary
    # we will change the date format to index depending on the timeframe
    if updated_timeframe == '1M' or updated_timeframe == '3M' or updated_timeframe == '6M' or \
            updated_timeframe == 'YTD':
        for date in index:
            month = date.date().month
            day = date.date().day
            date_index = f'{month}-{day}'
            new_index.append(date_index)
    else:
        for date in index:
            month = date.date().month
            year = str(date.date().year)[2:]
            date_index = f'{month}-{year}'
            new_index.append(date_index)

    for price in closing_prices:
        closing_reversed.append(price)

    # applying reformatted indices and reversed closing prices
    new_index.reverse()
    closing_reversed.reverse()
    data.index = new_index

    if adjusted_flag:
        data['5. adjusted close'] = closing_reversed
    else:
        data['4. close'] = closing_reversed

    return data, adjusted_flag


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
    data, meta_data = ts.get_weekly_adjusted(symbol=ticker)
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(years=-2))

    return data, meta_data


# returns a slice of the original dataset relevant for the past 5 years
def get_five_year_data(ticker, ts, current_time):
    data, meta_data = ts.get_weekly_adjusted(symbol=ticker)
    data = get_shortened_data(data, current_time + dateutil.relativedelta.relativedelta(years=-5))

    return data, meta_data


# goes through the data and keeps track of all the rows that have a date index >= limit
def get_shortened_data(data, limit):
    counter = 0
    dates = data.index

    if dates[-1].date() > limit.date():
        limit = dates[-1]

    for date in dates:
        if date.date() >= limit.date():
            counter += 1
        elif date.date().year == limit.date().year and date.date().month == limit.date().month and \
                date.date().day == limit.date().day:
            counter += 1
        else:
            break

    return data[:counter]


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
