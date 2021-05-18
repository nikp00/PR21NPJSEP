import os
import pandas as pd

from collections import defaultdict
result = {} 
result = defaultdict(lambda:0,result)

BASE_PATH = os.path.abspath(os.path.curdir)

for subdir, dirs, files in os.walk(os.path.join(BASE_PATH, "data", "date_count")):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".csv"):
            data = pd.read_csv(filepath)
            for row in data.iterrows():
                date = row[1]["date"]
                result[date] += row[1]["count"]    

df = pd.DataFrame.from_dict(result, orient="index")

df.to_csv(os.path.join(BASE_PATH, "data", "date_count_all.csv"))