import pandas as pd 
import numpy as np 
import json
from urllib.request import Request, urlopen

path = 'Json_Data/'

coin_list = pd.read_csv("CoinList.csv")

for coin in coin_list.itertuples():
    try:
        url = 'https://www.cointimemachine.com/api/v1/chart/' + coin.slug + '/rank/'
        data = pd.read_json(url)
        data.to_json(path + coin.slug + '_rank.json')
        print("Downloading Rank: " + coin.slug)
    except:
        print("Error Downloading Rank: " + coin.slug)

    try:
        req = Request('https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical?convert=USD,BTC&format=chart_crypto_details&id=' + str(coin.id) + '&interval=1d&time_end=2030-01-01&time_start=2013-04-28', headers={'User-Agent': 'Mozilla/5.0'})
        url = urlopen(req).read()
        data = pd.read_json(url)
        data.to_json(path + coin.slug + '_data.json')
        print("Downloading Market Data: " + coin.slug)
    except:
        print("Error Downloading Market Data: " + coin.slug)



