from pycoingecko import CoinGeckoAPI
import os
import pandas as pd
import requests
import json

import time
import datetime


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
    df.to_csv(path + "/" + symbol + "_price.csv", index=False)

    df = pd.DataFrame(columns=["date", "market_cap"], data=data["market_caps"])
    df.to_csv(path + "/" + symbol + "_market_cap.csv", index=False)

    df = pd.DataFrame(columns=["date", "volume"], data=data["total_volumes"])
    df.to_csv(path + "/" + symbol + "_volume.csv", index=False)

    print(f"{symbol} saved.")


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/"

    tracked_coins = pd.read_csv(path + "tracked_coins_details.csv")
    limit = tracked_coins["count"].quantile(0.75)
    tracked_coins = tracked_coins[tracked_coins["count"] >= limit]

    min_date = datetime.datetime.utcnow().timestamp()
    max_date = 0

    for source in os.listdir(path):
        if not os.path.isdir(path + source) or source == "price_data":
            continue

        for e in os.listdir(path + source):
            if os.path.isdir(path + source + "/" + e):
                for x in os.listdir(path + source + "/" + e):
                    if x.endswith(".csv"):
                        df = pd.read_csv(path + source + "/" + e + "/" + x)
                        c_min = df["date"].min()
                        c_max = df["date"].max()
            elif e.endswith(".csv"):
                df = pd.read_csv(path + source + "/" + e)
                c_min = df["date"].min()
                c_max = df["date"].max()

            if c_min < min_date:
                min_date = c_min
            if c_max > max_date:
                max_date = c_max

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
