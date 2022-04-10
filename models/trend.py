import hashlib
from dataclasses import dataclass
from typing import List

from models.article import Article


@dataclass()
class Trend:
    keyword: str
    score: float
    maxscore: float
    hashed: str
    delta: int
    topArticles: List[Article]

    DELTA_NEW = 999

    def __init__(self, keyword: str, score: float, maxscore: float, **kwargs) -> None:
        self.keyword = keyword
        self.score = score
        self.maxscore = maxscore
        self.hashed = Trend.get_hashed(keyword)
        self.delta = Trend.DELTA_NEW
        self.topArticles = []

    @staticmethod
    def get_hashed(keyword: str) -> str:
        hashed = hashlib.sha256(keyword.replace(" ", "").encode()).hexdigest()[:16]
        return hashed

    def add(self, score: float, maxscore: float) -> None:
        self.score += score
        self.maxscore = max(self.maxscore, maxscore)
