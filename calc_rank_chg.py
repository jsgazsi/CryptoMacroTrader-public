import pandas as pd 
import numpy as np 
import os 
import csv
import json
import datetime as dt 
from google.cloud import storage

#Set Values
path = 'Json_Data/'
CoinList = pd.read_csv('CoinList.csv')
bucket = "coin_data_bucket"
credentials = "gcs_credentials.json"
file_name = "rank_change.csv"


def processJson(df):
    df = pd.json_normalize(df['data']).replace(to_replace="null", value=np.NaN).dropna().ffill().sort_values('x')
    df = pd.DataFrame.from_dict(df).rename(columns= {'x': 'Date', 'y': 'Rank'}).set_index('Date')
    return df

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
    if np.isnan(change):
        change = 0
    return change

def upload_blob(bucket_name, file_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    storage_client = storage.Client.from_service_account_json(credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    print(
        "File {} uploaded to {}.".format(
            file_name, file_name
        )
    )





header = ["coin", "daily_chg", "daily_pct_chg", "week_chg", "week_pct_chg", "month_chg", "month_pct_chg", "quarter_chg", "quarter_pct_change", "biann_chg", "biann_pct_chg", "year_chg", "year_pct_chg", "composite_score"]
with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)


for coin in CoinList.itertuples():
    try:
        #Read in Data
        name = coin.name
        token = coin.slug
        data = getCoinRankData(token)
        #Process Data
        daily_chg = get_chg(data, "raw", 1)
        daily_pct_chg = get_chg(data, "pct", 1)
        week_chg = get_chg(data, "raw", 7)
        week_pct_chg = get_chg(data, "pct", 7)
        month_chg = get_chg(data, "raw", 30)
        month_pct_chg = get_chg(data, "pct", 30)
        quarter_chg = get_chg(data, "raw", 90)
        quarter_pct_chg = get_chg(data, "pct", 90)
        biann_chg = get_chg(data, "raw", 180)
        biann_pct_chg = get_chg(data, "pct", 180)
        year_chg = get_chg(data, "raw", 365)
        year_pct_chg = get_chg(data, "pct", 365)
        numerical_values = [daily_pct_chg,week_pct_chg,month_pct_chg,quarter_pct_chg,biann_pct_chg,year_pct_chg]
        composite_score = int(sum(numerical_values)/len(numerical_values))
        entry = [name, daily_chg, daily_pct_chg, week_chg, week_pct_chg, month_chg, month_pct_chg, quarter_chg, quarter_pct_chg, biann_chg, biann_pct_chg, year_chg, year_pct_chg, composite_score]
        print(entry)
        #Write Entry to file
        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(entry)
    except:
        print("Could not write data for: " + coin.slug)


try:
    upload_blob(bucket, file_name)
except:
    print("Error uploading, no such file?")





