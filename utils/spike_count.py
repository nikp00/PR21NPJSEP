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

COLOR_MAIN = "#363A45"
COLOR_MA_5 = "#FF9800"
COLOR_MA_8 = "#E040FB"
COLOR_MA_13 = "#9C27B0"
COLOR_VOLUME = "#B2B5BE"

LAG = 24
THRESHOLD = 5
INFLUENCE = 1
HOURDIFF = 12

TITLE_SIZE = 20
AXES_LABELS_SIZE = 15

plt.style.use("seaborn")


def date_parser(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))


def thresholding_algo(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0] * len(y)
    stdFilter = [0] * len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i - 1]) > threshold * stdFilter[i - 1]:
            if y[i] > avgFilter[i - 1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i - 1]
            avgFilter[i] = np.mean(filteredY[(i - lag + 1) : i + 1])
            stdFilter[i] = np.std(filteredY[(i - lag + 1) : i + 1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i - lag + 1) : i + 1])
            stdFilter[i] = np.std(filteredY[(i - lag + 1) : i + 1])

    return dict(
        signals=np.asarray(signals),
        avgFilter=np.asarray(avgFilter),
        stdFilter=np.asarray(stdFilter),
    )


def count_spike_diff(mentions, price, hourdiff):
    counter = 0
    for i, element in enumerate(mentions):
        if element == 1.0:
            if i + hourdiff > price.size:
                end = price.size
            else:
                end = i + hourdiff
            if 1.0 in price[i + 1 : end]:
                counter += 1
    return counter


tracked_coins = pd.read_csv(
    open(os.path.join(BASE_PATH, "data/tracked_coins_details.csv"))
)

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
        open(
            os.path.join(PRICE_DATA_DIR, TRACKED_COIN, f"{TRACKED_COIN}_price.csv"), "r"
        ),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )

    result_mentions = thresholding_algo(
        mentions_data["count"], lag=LAG, threshold=THRESHOLD, influence=INFLUENCE
    )

    print(TRACKED_COIN)
    result_price = thresholding_algo(
        price_data["price"], lag=LAG, threshold=THRESHOLD, influence=INFLUENCE
    )

    result[TRACKED_COIN] = count_spike_diff(
        result_mentions["signals"], result_price["signals"], hourdiff=HOURDIFF
    )

df = pd.DataFrame.from_dict(result, orient="index", columns=["count"]).sort_values(
    "count", ascending=False
)

df.to_csv(BASE_PATH + "/data/spike_count.csv")

if not os.path.exists(os.path.join(BASE_PATH, "visualization/spikes")):
    os.mkdir(os.path.join(BASE_PATH, "visualization/spikes"))


for pos, e in enumerate(df.index):
    TRACKED_COIN = e
    fig, ax = plt.subplots(2, 1, figsize=(20, 14))

    mentions_data = pd.read_csv(
        open(os.path.join(MENTIONS_COUNT_DIR, f"{TRACKED_COIN}.csv"), "r"),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )

    price_data = pd.read_csv(
        open(
            os.path.join(PRICE_DATA_DIR, TRACKED_COIN, f"{TRACKED_COIN}_price.csv"), "r"
        ),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )

    volume_data = pd.read_csv(
        open(
            os.path.join(PRICE_DATA_DIR, TRACKED_COIN, f"{TRACKED_COIN}_volume.csv"),
            "r",
        ),
        parse_dates=True,
        date_parser=date_parser,
        index_col="date",
    )

    result_mentions = thresholding_algo(
        mentions_data["count"], lag=LAG, threshold=THRESHOLD, influence=INFLUENCE
    )

    result_price = thresholding_algo(
        price_data["price"], lag=LAG, threshold=THRESHOLD, influence=INFLUENCE
    )

    ax[0].plot(mentions_data["count"], label="Mentions count")
    ax[0].plot(
        mentions_data.index,
        result_mentions["avgFilter"],
        label="Mooving average",
        color="#f55c47",
    )
    ax[0].plot(
        mentions_data.index,
        result_mentions["avgFilter"] + THRESHOLD * result_mentions["stdFilter"],
        color="#9fe6a0",
    )
    ax[0].plot(
        mentions_data.index,
        result_mentions["avgFilter"] - THRESHOLD * result_mentions["stdFilter"],
        color="#9fe6a0",
    )

    ax[0].fill_between(
        mentions_data.index,
        result_mentions["avgFilter"] + THRESHOLD * result_mentions["stdFilter"],
        result_mentions["avgFilter"] - THRESHOLD * result_mentions["stdFilter"],
        color="#9fe6a0",
        alpha=0.2,
        label=f"Threshold (mean +- {THRESHOLD} * std)",
    )

    ax2 = ax[1].twinx()
    ax2.bar(
        height=volume_data["volume"],
        x=volume_data.index,
        color=COLOR_VOLUME,
        label="Volume",
        width=0.06,
    )

    ax[1].plot(price_data["price"], label="Price")

    for i, (sig, date) in enumerate(
        zip(result_mentions["signals"], mentions_data.index)
    ):
        if sig == 1 and i < len(price_data):
            ax[1].plot(
                datetime.datetime.fromisoformat(str(date)),
                price_data.iloc[i]["price"],
                "ro",
                label="Spike marker",
            )

    ax[0].set_title("Z-Score peak detection of mentions", fontsize=TITLE_SIZE)
    ax[0].set_ylabel("Number of mentions", fontsize=AXES_LABELS_SIZE)
    ax[0].set_xlabel("Time", fontsize=AXES_LABELS_SIZE)
    ax[0].legend()

    h1, l1 = ax[1].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    ax[1].set_title(
        f"{TRACKED_COIN} price and spike detection markers", fontsize=TITLE_SIZE
    )
    ax[1].set_ylabel("Price [USD]", fontsize=AXES_LABELS_SIZE)
    ax[1].set_xlabel("Time", fontsize=AXES_LABELS_SIZE)
    ax[1].legend(h2 + list(h1)[0:2], l2 + list(l1)[0:2])
    ax[1].set_zorder(ax2.get_zorder() + 1)
    ax[1].patch.set_visible(False)

    ax2.grid(b=None)
    ax2.patch.set_visible(True)
    ax2.set_ylabel("Volume", fontsize=AXES_LABELS_SIZE)

    fig.suptitle(TRACKED_COIN, fontsize=22)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.savefig(
        os.path.join(
            BASE_PATH, "visualization/spikes", f"{pos+1}_{TRACKED_COIN}_spike.png"
        )
    )
    plt.close(fig)
