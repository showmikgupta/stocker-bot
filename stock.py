import os
import requests
import pandas as pd
from dotenv import load_dotenv #used for getting environment vars
from alpha_vantage.timeseries import TimeSeries #python access to alpha vantahe api
import matplotlib.pyplot as plt

load_dotenv()
AV_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

def get_month_chart(ticker):
	ts = TimeSeries(key=AV_KEY, output_format='pandas')
	data, meta_data = ts.get_daily(symbol=ticker)
	data = data[0:23]
	data['4. close'].plot()
	plt.title(f'Month Chart for {ticker}')
	plt.savefig(f'{ticker.lower()}_month_chart.png')
	plt.clf()
