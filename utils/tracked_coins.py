from pycoingecko import CoinGeckoAPI
import os
import pandas as pd
from threading import Thread
from collections import defaultdict
import requests
import json
import numpy as np
import datetime


class Parser(Thread):
    def __init__(self, path, coins_symbol, coins_name, blacklist):
        super(Parser, self).__init__()
        self.path = path
        self.counter = defaultdict(int)
        self.coins_symbol = coins_symbol
        self.coins_name = coins_name
        self.tracked_coins = set()
        self.blacklist = blacklist

        self.date_counter = defaultdict(lambda: defaultdict(int))

    def run(self):
        print(self.path[len(self.path) - self.path[::-1].index("/") :])
        df = pd.read_csv(self.path)
        for index, e in df.iterrows():
            if type(e["content"]) == float:
                continue
            content = (
                set(map(lambda x: x.upper(), e["content"].split(" "))) - self.blacklist
            )

            date = self.convert_timestamp(e["date"])

            for k in content & self.coins_symbol:
                self.counter[k] += 1
                self.date_counter[k][date] += 1

            for k in content & set(self.coins_name.keys()):
                self.counter[self.coins_name[k]] += 1
                self.date_counter[self.coins_name[k]][date] += 1

            self.tracked_coins |= (content & self.coins_symbol) | (
                content & set(self.coins_name.keys())
            )

    def convert_timestamp(self, x):
        x = datetime.datetime.fromtimestamp(x)
        x = x.replace(minute=0, second=0, microsecond=0)
        x = int(datetime.datetime.timestamp(x))
        return x


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
    data = list()
    for i in range(1, 5):
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={i}"
        ).json()
        data.extend(r)

    coins_symbol = {e["symbol"].upper() for e in data}
    coins_name = {e["name"].upper(): e["symbol"].upper() for e in data}
    coins_id = {e["symbol"].upper(): e["id"] for e in data}

    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/"

    tracked_coins = set()
    threads = list()
    counter = defaultdict(int)

    blacklist = pd.read_csv(os.path.join(path, "3000_most_common_english_words.csv"))
    blacklist = set(map(lambda x: x.upper(), blacklist.values.flatten()))

    min_date, max_date = find_min_max_date(path)
    print(f"Start date: {min_date}, end date: {max_date}")

    for source in os.listdir(os.path.join(path, "posts")):
        if not os.path.isdir(os.path.join(path, "posts", source)):
            continue

        for e in os.listdir(os.path.join(path, "posts", source)):
            if os.path.isdir(os.path.join(path, "posts", source, e)):
                for x in os.listdir(os.path.join(path, "posts", source, e)):
                    if x.endswith(".csv"):
                        threads.append(
                            Parser(
                                os.path.join(path, "posts", source, e, x),
                                coins_symbol,
                                coins_name,
                                blacklist,
                            )
                        )
            elif e.endswith(".csv"):
                threads.append(
                    Parser(
                        os.path.join(path, "posts", source, e),
                        coins_symbol,
                        coins_name,
                        blacklist,
                    )
                )

    print("started")

    for e in threads:
        e.start()

    for e in threads:
        e.join()

    date_counter = defaultdict(lambda: defaultdict(int))
    for e in threads:
        tracked_coins |= e.tracked_coins
        for k, v in e.counter.items():
            counter[k] += v
        for symbol, data in e.date_counter.items():
            for date, count in data.items():
                date_counter[symbol][date] += count

    for k, v in counter.items():
        counter[k] = [v, coins_id[k]]

    print("Parsing done.")

    counter_df = (
        pd.DataFrame.from_dict(
            columns=["count", "id"],
            data=counter,
            orient="index",
        )
        .reset_index()
        .rename(columns={"index": "symbol"})
        .sort_values(by="count", ascending=False)
    )

    tracked_coins_df = pd.DataFrame(columns=["symbol"], data=tracked_coins)
    print("Saved tracked_coins.csv")

    counter_df.to_csv(
        open(os.path.join(path, "tracked_coins_details.csv"), "w"),
        index=False,
    )

    tracked_coins_df.to_csv(
        open(os.path.join(path, "tracked_coins.csv"), "w"),
        index=False,
    )
    print("Saved tracked_coins_details.csv")

    if not os.path.exists(os.path.join(path, "date_count")):
        os.mkdir(os.path.join(path, "date_count"))

    date_range = pd.date_range(
        start=datetime.datetime.fromtimestamp(min_date),
        end=datetime.datetime.fromtimestamp(max_date),
        freq="H",
    )

    date_range = [int(datetime.datetime.timestamp(e)) for e in date_range]
    for i, (symbol, data) in enumerate(date_counter.items()):
        df_data = list()
        for e in date_range:
            if e in data.keys():
                df_data.append([e, data[e]])
            else:
                df_data.append([e, 0])

        df = pd.DataFrame(columns=["date", "count"], data=df_data)
        df.to_csv(
            open(os.path.join(path, "date_count", f"{symbol}.csv"), "w"), index=False
        )

        print(f"Saved date_count for {symbol} ({i}/{len(date_counter)})")
