import os
from dotenv import load_dotenv  # used for getting environment vars
from alpha_vantage.timeseries import TimeSeries  # python access to alpha vantahe api
import matplotlib.pyplot as plt

load_dotenv()
AV_KEY = os.getenv('ALPHAVANTAGE_API_KEY')


# get month data for give ticker using alpha vantage api plotting daily closing prices
# using pyplot to plot pandas dataframe
def get_month_chart(ticker):
    ts = TimeSeries(key=AV_KEY, output_format='pandas')
    data, meta_data = ts.get_daily(symbol=ticker)
    data = data[0:23]
    data['4. close'].plot()
    plt.title(f'Month Chart for {ticker}')
    plt.savefig(f'{ticker.lower()}_month_chart.png')
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
