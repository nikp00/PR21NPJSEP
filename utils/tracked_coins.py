from pycoingecko import CoinGeckoAPI
import os
import pandas as pd
from threading import Thread
from collections import defaultdict
import requests
import json


class Parser(Thread):
    def __init__(self, path, coins_symbol, coins_name, blacklist):
        super(Parser, self).__init__()
        self.path = path
        self.counter = defaultdict(int)
        self.coins_symbol = coins_symbol
        self.coins_name = coins_name
        self.tracked_coins = set()
        self.blacklist = blacklist

    def run(self):
        print(self.path[len(self.path) - self.path[::-1].index("/") :])
        df = pd.read_csv(self.path)
        for index, e in df.iterrows():
            if type(e["content"]) == float:
                continue
            content = (
                set(map(lambda x: x.upper(), e["content"].split(" "))) - self.blacklist
            )

            for k in content & self.coins_symbol:
                self.counter[k] += 1

            for k in content & set(self.coins_name.keys()):
                self.counter[self.coins_name[k]] += 1

            self.tracked_coins |= (content & self.coins_symbol) | (
                content & set(self.coins_name.keys())
            )


if __name__ == "__main__":
    data = list()
    for i in range(1, 5):
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={i}"
        ).json()
        data.extend(r)

    coins_symbol = {e["symbol"].upper() for e in data}
    coins_name = {e["name"].upper(): e["symbol"].upper() for e in data}

    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/"

    tracked_coins = set()
    threads = list()
    counter = defaultdict(int)

    blacklist = pd.read_csv(path + "3000_most_common_english_words.csv")
    blacklist = set(map(lambda x: x.upper(), blacklist["a"]))

    for source in os.listdir(path):
        if not os.path.isdir(path + source):
            continue

        for e in os.listdir(path + source):
            if os.path.isdir(path + source + "/" + e):
                for x in os.listdir(path + source + "/" + e):
                    if x.endswith(".csv"):
                        threads.append(
                            Parser(
                                path + source + "/" + e + "/" + x,
                                coins_symbol,
                                coins_name,
                                blacklist,
                            )
                        )
            elif e.endswith(".csv"):
                threads.append(
                    Parser(path + source + "/" + e, coins_symbol, coins_name, blacklist)
                )
    print("started")

    for e in threads:
        e.start()

    for e in threads:
        e.join()

    print("Done")
    for e in threads:
        tracked_coins |= e.tracked_coins
        for k, v in e.counter.items():
            counter[k] += v

    counter_df = (
        pd.DataFrame.from_dict(
            columns=["count"],
            data=counter,
            orient="index",
        )
        .reset_index()
        .rename(columns={"index": "symbol"})
        .sort_values(by="count", ascending=False)
    )

    tracked_coins_df = pd.DataFrame(columns=["symbol"], data=tracked_coins)

    counter_df.to_csv(
        open(path + "tracked_coins_count.csv", "w"),
        index=False,
    )

    tracked_coins_df.to_csv(
        open(path + "tracked_coins.csv", "w"),
        index=False,
    )
