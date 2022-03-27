import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from src import Trend, calculate_trends
from src.crawl import set_delta

TREND_FILE = "data/trends.json"
INTERVAL_SECS = 600


class TrendJson:
    @classmethod
    def read(cls) -> Dict:
        if os.path.isfile(TREND_FILE):
            with open(TREND_FILE, "r") as trend_json:
                cls.json_dict = json.load(trend_json)
        else:
            cls.json_dict = {}

    @classmethod
    def write(cls):
        with open(TREND_FILE, "w") as trend_json:
            json.dump(cls.json_dict, trend_json, ensure_ascii=False, indent=4)

    @classmethod
    def update(cls, key: str, value: Union[List, Dict], json_dict: Any = None) -> Dict:
        if json_dict == None:
            json_dict = cls.json_dict
        keys = key.strip("/").split("/")
        selected_key = keys[0]
        if len(keys) == 1:
            json_dict[selected_key] = value
        elif len(keys) >= 2:
            selected_dict = json_dict.get(selected_key, {})
            json_dict[selected_key] = TrendJson.update(
                "/".join(keys[1:]), value, selected_dict
            )

        return json_dict

    @classmethod
    def get(cls, key: str, default: Any, json_dict: Any = None) -> Dict:
        if json_dict == None:
            json_dict = cls.json_dict
        if key == None:
            return json_dict

        keys = key.strip("/").split("/")
        selected_key = keys[0]
        if selected_key not in json_dict.keys():
            return default

        json_dict = json_dict[selected_key]
        if len(keys) >= 2:
            return TrendJson.get("/".join(keys[1:]), default, json_dict)
        return json_dict

    @classmethod
    def delete(cls, key: str, json_dict: Any = None) -> Dict:
        if json_dict == None:
            json_dict = cls.json_dict
        if key == None:
            return None

        keys = key.strip("/").split("/")
        selected_key = keys[0]
        if selected_key not in json_dict.keys():
            return

        if len(keys) == 1:
            del json_dict[selected_key]
        elif len(keys) >= 2:
            json_dict[selected_key] = TrendJson.delete(
                "/".join(keys[1:]), json_dict[selected_key]
            )
            if TrendJson.get(f"{selected_key}/{keys[1]}", None, json_dict) == {}:
                json_dict = TrendJson.delete(f"{selected_key}/{keys[1]}", json_dict)
        return json_dict


if __name__ == "__main__":
    TrendJson.read()

    new_timestamp = int(datetime.now(timezone.utc).timestamp())
    new_trends = calculate_trends()

    timestamps: List[int] = TrendJson.get("timestamps", [])
    old_timestamps = []
    if timestamps:
        old_timestamps = sorted(
            [timestamp for timestamp in timestamps if timestamp <= new_timestamp - INTERVAL_SECS],
            reverse=True,
        )
    old_trends = []
    if old_timestamps:
        old_trends = [
            Trend(**trend) for trend in TrendJson.get(str(old_timestamps[0]), None) if trend
        ]

    new_trends = set_delta(new_trends, old_trends)
    new_trends_dict = [vars(trend) for trend in new_trends]
    print(new_trends_dict)
    TrendJson.update(str(new_timestamp), new_trends_dict)

    if len(old_timestamps) >= 2:
        for old_timestamp in old_timestamps[1:]:
            TrendJson.delete(str(old_timestamp))
        timestamps = list(set(timestamps) - set(old_timestamps[1:]))
    timestamps.append(new_timestamp)
    TrendJson.update("timestamps", timestamps)

    TrendJson.write()
