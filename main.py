from datetime import datetime, timezone
from typing import List

from models.trend import Trend
from src import calculate_trends
from src.crawl import set_delta, update_top_articles
from src.trendjson import TrendJson

INTERVAL_SECS = 600

if __name__ == "__main__":
    TrendJson.read()

    new_timestamp = int(datetime.now(timezone.utc).timestamp())
    new_trends = calculate_trends()

    timestamps: List[int] = TrendJson.get("timestamps", [])
    old_timestamps = []
    if timestamps:
        old_timestamps = sorted(
            [
                timestamp
                for timestamp in timestamps
                if timestamp <= new_timestamp - INTERVAL_SECS
            ],
            reverse=True,
        )
    old_trends = []
    if old_timestamps:
        old_trends = [
            Trend(**trend)
            for trend in TrendJson.get(str(old_timestamps[0]), None)
            if trend
        ]

    new_trends = set_delta(new_trends, old_trends)
    new_trends = update_top_articles(new_trends)
    new_trends_dict = [trend.__dict__ for trend in new_trends]
    print(new_trends_dict)
    TrendJson.update(str(new_timestamp), new_trends_dict)

    if len(old_timestamps) >= 2:
        for old_timestamp in old_timestamps[1:]:
            TrendJson.delete(str(old_timestamp))
        timestamps = list(set(timestamps) - set(old_timestamps[1:]))
    timestamps.append(new_timestamp)
    TrendJson.update("timestamps", timestamps)

    TrendJson.write()
