import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import os
import numpy as np

BASE_PATH = os.path.abspath(os.path.curdir)
PRICE_DATA_DIR = os.path.join(BASE_PATH, "data/price_data/")
MENTIONS_COUNT_DIR = os.path.join(BASE_PATH, "data/date_count")
TRACKED_COIN_DIR = os.path.join(BASE_PATH, "data/tracked_coins")

MIN_DATE = "2021-02-01 00:00:00"
MAX_DATE = "2021-03-31 23:00:00"

lag = 24
threshold = 5
influence = 1
hourdiff = 12

def date_parser(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))

def thresholding_algo(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))

def count_spike_diff(mentions, price, hourdiff):
    counter = 0
    for i, element in enumerate(mentions):
        if element == 1.0:
            if i+hourdiff > price.size:
                end = price.size
            else:
                end = i+hourdiff
            if 1.0 in price[i+1:end]:
                counter += 1        
    return counter            

tracked_coins = pd.read_csv(open(os.path.join(BASE_PATH, "data/tracked_coins_details.csv")))

limit = tracked_coins["count"].quantile(0.75)
tracked_coins = tracked_coins[tracked_coins["count"] >= limit]

result = dict()

for coin in tracked_coins.symbol:

    TRACKED_COIN = coin

    mentions_data = pd.read_csv(
        open(os.path.join(MENTIONS_COUNT_DIR, f"{TRACKED_COIN}.csv"), "r"),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )

    price_data = pd.read_csv(
        open(os.path.join(PRICE_DATA_DIR, TRACKED_COIN, f"{TRACKED_COIN}_price.csv"), "r"),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )
    
    result_mentions = thresholding_algo(mentions_data["count"], lag=lag, threshold=threshold, influence=influence)

    result_price = thresholding_algo(price_data["price"], lag=lag, threshold=threshold, influence=influence)

    result[TRACKED_COIN] = count_spike_diff(result_mentions["signals"],result_price["signals"],hourdiff=hourdiff)

pd.DataFrame.from_dict(result, orient='index', columns=['count']).sort_values("count",ascending=False).to_csv(BASE_PATH + "/data/spike_count.csv")