import os
import pandas as pd

import time
import datetime

if __name__ == "__main__":
    path = os.path.dirname(__file__)
    path = path[0 : len(path) - path[::-1].index("/")] + "data/discord/"
    for e in os.listdir(path):
        if not e.endswith(".csv"):
            continue
        df = pd.read_csv(path + e)
        df["date"] = df["date"].apply(
            lambda x: int(
                datetime.datetime.timestamp(
                    datetime.datetime.fromisoformat(
                        x[0 : x.index("+") - 1] + x[x.index("+") :]
                    )
                )
            )
        )
        df.to_csv(path + e, index=False)