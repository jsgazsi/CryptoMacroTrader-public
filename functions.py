from google.cloud import storage
import pandas as pd 
import numpy as np 
import io
from io import BytesIO
import datetime as dt 


def processJson(df):
    df = pd.json_normalize(df['data']).replace(to_replace="null", value=np.NaN).dropna().ffill().sort_values('x')
    df = pd.DataFrame.from_dict(df).rename(columns= {'x': 'Date', 'y': 'Rank'}).set_index('Date')
    return df

def getJson(name):
    storage_client = storage.Client.from_service_account_json("gcs_credentials.json")
    BUCKET_NAME = "coin_data_bucket"
    PATH = "Json_Data/"
    bucket = storage_client.bucket(BUCKET_NAME)
    blop = bucket.blob(PATH + name)
    data = blop.download_as_string()
    json = pd.read_json(io.BytesIO(data))
    return json

def getCoinRankData(token):
    myFile = "Json_Data/" + token + "_rank.json"
    data = pd.read_json(myFile)
    rank_data = processJson(data)
    rank_data.index = pd.to_datetime(rank_data.index).date
    today = dt.datetime.today().strftime('%Y-%m-%d')
    date_range = pd.date_range("01-01-2015", today)
    idx = pd.DatetimeIndex(date_range)
    rank_data = rank_data.reindex(idx)
    rank_data.interpolate('pad',inplace=True)
    rank_data.dropna(inplace=True)
    return rank_data

def get_chg(df, str, int):
    if str == "pct":
        change = df.pct_change(periods=int) * -100
        change = change.round(1)
        change = (change.iloc[-1][0])
    elif str == "raw":
        change = df.diff(periods=int) * -1
        change = (change.iloc[-1][0])
        #change = int(change)
    return change
