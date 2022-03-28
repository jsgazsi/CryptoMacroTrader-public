import pandas as pd 
import json
from urllib.request import Request, urlopen
from google.cloud import storage


path = 'Json_Data/'
rank_suffix = '_rank.json'
data_suffix = '_data.json'
bucket = 'coin_data_bucket'
credentials = "gcs_credentials.json"
coin_list = pd.read_csv("CoinList.csv")


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


for coin in coin_list.itertuples():
    try:
        token = coin.slug
        rank_filename = path + token + rank_suffix
        data_filename = path + token + data_suffix
        upload_blob(bucket, rank_filename)
        upload_blob(bucket, data_filename)
    except:
        print("File not Found:" + token)
