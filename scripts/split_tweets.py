#!/usr/bin/env python3
"""
Split tweets.json into per-year files for on-demand loading.
Outputs assets/data/tweets-{year}.json for each year.
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
TWEETS_JSON = BASE_DIR / "_data" / "tweets.json"
DATA_DIR = BASE_DIR / "assets" / "data"

with open(TWEETS_JSON) as f:
    tweets = json.load(f)

by_year = defaultdict(list)
for tweet in tweets:
    year = tweet.get('date', '')[:4] or 'unknown'
    by_year[year].append(tweet)

DATA_DIR.mkdir(parents=True, exist_ok=True)

for year, year_tweets in sorted(by_year.items()):
    out_path = DATA_DIR / f"tweets-{year}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(year_tweets, f, ensure_ascii=False)
    size_kb = out_path.stat().st_size / 1024
    print(f"  {year}: {len(year_tweets):5d} tweets → {out_path.name} ({size_kb:.0f} KB)")

print(f"\nDone. {len(tweets)} tweets split into {len(by_year)} files.")
