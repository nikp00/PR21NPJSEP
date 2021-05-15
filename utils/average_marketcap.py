import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import numpy as np

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
    rects1 = ax.bar(x - width/2, sortedDf["mention_percentage"][1:20], width, label='Obembe')
    rects2 = ax.bar(x + width/2, sortedDf["market_cap_percentage"][1:20], width, label='Tržna kapitalizacija')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('%')
    ax.set_title('Odstotek obemb proti odstotku tržne kapitalizacije (razporejeno po največji razliki)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels,rotation=90)
    ax.legend()

    fig.tight_layout()

    plt.show()