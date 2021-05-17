from pycoingecko import CoinGeckoAPI
import os
import pandas as pd
import requests
import json

import time
import datetime


def convert_time(x, micros=False):
    if micros:
        x = datetime.datetime.fromtimestamp(x / 1000.0)
    else:
        x = datetime.datetime.fromtimestamp(x)
    x = x.replace(minute=0, second=0, microsecond=0)
    x = int(datetime.datetime.timestamp(x))
    return x


def get_data(symbol, symbol_id, start, end, path):

    r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart/range?vs_currency=usd&from={start}&to={end}"
    )

    status = r.status_code
    print(status)
    while status != 200:
        time.sleep(20)
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart/range?vs_currency=usd&from={start}&to={end}"
        )
        status = r.status_code
        print(status)

    data = r.json()

    df = pd.DataFrame(columns=["date", "price"], data=data["prices"])
    df["date"] = df["date"].apply(lambda x: convert_time(x, micros=True))
    df = df.drop_duplicates(subset="date")
    df.to_csv(path + "/" + symbol + "_price.csv", index=False)

    df = pd.DataFrame(columns=["date", "market_cap"], data=data["market_caps"])
    df["date"] = df["date"].apply(lambda x: convert_time(x, micros=True))
    df = df.drop_duplicates(subset="date")
    df.to_csv(path + "/" + symbol + "_market_cap.csv", index=False)

    df = pd.DataFrame(columns=["date", "volume"], data=data["total_volumes"])
    df["date"] = df["date"].apply(lambda x: convert_time(x, micros=True))
    df = df.drop_duplicates(subset="date")
    df.to_csv(path + "/" + symbol + "_volume.csv", index=False)

    print(f"{symbol} saved.")


def find_min_max_date(path):
    min_date = datetime.datetime.utcnow().timestamp()
    max_date = 0
    path = os.path.join(path, "posts")
    print(path)
    for source in os.listdir(path):
        if not os.path.isdir(os.path.join(path, source)):
            continue

        for e in os.listdir(os.path.join(path, source)):
            if os.path.isdir(os.path.join(path, source, e)):
                for x in os.listdir(os.path.join(path, source, e)):
                    if x.endswith(".csv"):
                        df = pd.read_csv(os.path.join(path, source, e, x))
                        c_min = df["date"].min()
                        c_max = df["date"].max()
            elif e.endswith(".csv"):
                df = pd.read_csv(os.path.join(path, source, e))
                c_min = df["date"].min()
                c_max = df["date"].max()

            if c_min < min_date:
                min_date = c_min
            if c_max > max_date:
                max_date = c_max

    print(min_date, max_date)
    min_date = datetime.datetime.fromtimestamp(min_date)
    min_date = min_date.replace(minute=0, second=0, microsecond=0)
    min_date = int(datetime.datetime.timestamp(min_date))

    max_date = datetime.datetime.fromtimestamp(max_date)
    max_date = max_date.replace(minute=0, second=0, microsecond=0)
    max_date = int(datetime.datetime.timestamp(max_date))

    return min_date, max_date


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/"

    tracked_coins = pd.read_csv(path + "tracked_coins_details.csv")
    limit = tracked_coins["count"].quantile(0.75)
    tracked_coins = tracked_coins[tracked_coins["count"] >= limit]

    min_date, max_date = find_min_max_date(path)

    if not os.path.exists(path + "price_data"):
        os.mkdir(path + "price_data")

    for index, coin in tracked_coins.iterrows():
        symbol = coin["symbol"]
        symbol_id = coin["id"]
        if not os.path.exists(path + "price_data/" + symbol):
            os.mkdir(path + "price_data/" + symbol)
        get_data(symbol, symbol_id, min_date, max_date, path + "price_data/" + symbol)

    print(
        "Date range saved: ",
        datetime.datetime.fromtimestamp(max_date)
        - datetime.datetime.fromtimestamp(min_date),
    )
