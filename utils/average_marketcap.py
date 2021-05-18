import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import datetime
from collections import defaultdict

import os

BASE_PATH = os.path.abspath(os.path.curdir)
PRICE_DATA_DIR = os.path.join(BASE_PATH, "data/price_data/")
MENTIONS_COUNT_DIR = os.path.join(BASE_PATH, "data/date_count")

COLOR_MAIN = "#363A45"
COLOR_MA_5 = "#FF9800"
COLOR_MA_8 = "#E040FB"
COLOR_MA_13 = "#9C27B0"
COLOR_VOLUME = "#B2B5BE"

MIN_DATE = "2021-02-01 00:00:00"
MAX_DATE = "2021-04-05 03:00:00"

TITLE_SIZE = 20
AXES_LABELS_SIZE = 15

DATE_RANGE = pd.date_range(
    start=MIN_DATE,
    end=MAX_DATE,
    freq="2D",
)

plt.style.use("seaborn")

if __name__ == "__main__":
    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/"

    tracked_coins = pd.read_csv(path + "tracked_coins_details.csv")
    limit = tracked_coins["count"].quantile(0.75)
    tracked_coins = tracked_coins[tracked_coins["count"] >= limit]

    avg_cap = dict()

    for coin in tracked_coins.iterrows():
        symbol = coin[1]["symbol"]
        newpath = '%sprice_data/%s/%s_market_cap.csv'%(path,symbol,symbol)
        coin_data = pd.read_csv(newpath)
        
        avg_cap[symbol] = (np.average(coin_data["market_cap"]))
 
    avg_cap = (pd.DataFrame(avg_cap.items(), columns=['symbol', 'avg_market_cap']))
    total_market_cap = (np.sum(avg_cap["avg_market_cap"]))

    total_mentions = (np.sum(tracked_coins["count"]))
    mention_percentage = (tracked_coins["count"] / total_mentions)
    market_cap_percentage = (avg_cap["avg_market_cap"] / total_market_cap)

    diff = mention_percentage - market_cap_percentage

    tracked_coins["diff"] = diff
    tracked_coins["mention_percentage"] = mention_percentage
    tracked_coins["market_cap_percentage"] = market_cap_percentage

    sortedDf = tracked_coins.sort_values(by="diff",key=abs)[::-1]


    labels = sortedDf["symbol"][1:20]#[np.r_[:1, 2:20]]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, sortedDf["mention_percentage"][1:20], width, label='Mentions')
    rects2 = ax.bar(x + width/2, sortedDf["market_cap_percentage"][1:20], width, label='Market cap')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('%')
    ax.set_title('Percentage of mentions in comparison to market capitalisation')
    ax.set_xticks(x)
    ax.set_xticklabels(labels,rotation=90)
    ax.legend()

    fig.tight_layout()

    plt.savefig(
        os.path.join(
            BASE_PATH, "visualization/", "market_cap_vs_mentions.png"
        )
    )
    plt.close(fig)