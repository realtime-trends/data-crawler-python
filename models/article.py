import json
from dataclasses import dataclass


@dataclass()
class Article:
    title: str
    link: str
    content: str
    thumnail: str

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
