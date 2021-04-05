import praw
import pandas as pd
import numpy as np
import re
import unicodedata
import os
import threading
import time
import random


class Scraper(threading.Thread):
    def __init__(self, subreddit, query, limit):
        super(Scraper, self).__init__()
        self.reddit = praw.Reddit(
            client_id="zp34e692mUMjeA",  # your client id
            client_secret="yIhRJjlZ6jTfCij9ewUH0pjHYcgq_A",  # your client secret
            user_agent="PR2021",  # user agent name
            username=os.environ["REDDIT_USERNAME"],  # your reddit username
            password=os.environ["REDDIT_PASSWORD"],
        )
        self.subreddit = subreddit
        self.query = query
        self.limit = limit

    def run(self):

        path = os.path.dirname(__file__)
        path = path[0 : len(path) - path[::-1].index("/")] + "data/reddit/"

        # for sub, query, interval in subreddits:
        if not os.path.exists(path + self.subreddit):
            os.mkdir(path + self.subreddit)

        for post in self.reddit.subreddit(self.subreddit).search(
            self.query, limit=self.limit
        ):
            comments_dict = {
                "date": [],  # created_utc
                "content": [],  # body
                "score": [],  # score
            }
            for i in range(1, 33):
                post.comments.replace_more(limit=3, threshold=5)
                time.sleep(1.5)

            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                comments_dict["date"].append(int(comment.created_utc))
                comments_dict["content"].append(re.sub("[^\S ]+", " ", comment.body))
                comments_dict["score"].append(comment.score)
            df = pd.DataFrame(comments_dict)
            df.to_csv(
                open(
                    path + self.subreddit + "/" + self.slugify(post.title) + ".csv", "w"
                ),
                index=False,
            )
            time.sleep(10)
            print(f"{self.getName()}: {post.title} saved")

    def slugify(self, value, allow_unicode=False):
        """
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize("NFKC", value)
        else:
            value = (
                unicodedata.normalize("NFKD", value)
                .encode("ascii", "ignore")
                .decode("ascii")
            )
        value = re.sub(r"[^\w\s-]", "", value.lower())
        return re.sub(r"[-\s]+", "-", value).strip("-_")


if __name__ == "__main__":
    subreddits = [
        ("CryptoCurrency", "Daily discussion", 31),
        ("CryptoMarkets", "Weekly Discussion", 5),
        ("SatoshiStreetBets", "Daily Discussion", 31),
        ("binance", "Weekly Discussion", 5),
    ]
    scrapers = []

    for e in subreddits:
        print(*e)
        s = Scraper(*e)
        s.setName(e[0])
        scrapers.append(s)

    print("----------------------------")
    print("----------------------------")

    for e in scrapers:
        e.start()
