import re
import warnings
from typing import Dict, List
from urllib import parse

import hanja
import requests
from bs4 import BeautifulSoup
from models.article import Article
from models.trend import Trend

WEIGHTS = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11]
ENGINE_BIAS = {
    "nate": 0.7,
    "zum": 1.0,
}
SIMILARITY_WEIGHT = 0.7
IGNORE_SYMBOLS = r"[!@#$%^&*\(\)\[\]\{\};:,./<>?\|`]"


def process_keyword(keyword: str):
    keyword = re.sub(IGNORE_SYMBOLS, " ", keyword)
    keyword = re.sub(r" +", " ", keyword)
    keyword = hanja.translate(keyword, "substitution")
    return keyword


def get_trends_by_engine(engine: str) -> List[Trend]:
    trends: List[Trend] = []
    keywords: List[str] = []

    if engine == "zum":
        url = "https://search.zum.com/search.zum?query="
        req = requests.get(url)
        if req.status_code == 200:
            html = req.text
            soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
            for s in soup.select(
                "#issue_wrap > ul > li > div > a:nth-child(1) > span.txt"
            ):
                keyword = process_keyword(s.text)
                keywords.append(keyword)
    elif engine == "nate":
        url = "https://www.nate.com/js/data/jsonLiveKeywordDataV1.js"
        req = requests.get(url)
        if req.status_code == 200:
            req.encoding = "euc-kr"
            for j in req.json():
                keyword = process_keyword(j[1])
                keywords.append(keyword)
    for index, keyword in enumerate(keywords):
        score = WEIGHTS[index] * ENGINE_BIAS[engine]
        trends.append(Trend(keyword, score, score))
    return trends


def set_delta(new_trends: List[Trend], old_trends: List[Trend]):
    for new_index, new_trend in enumerate(new_trends):
        for old_index, old_trend in enumerate(old_trends):
            if new_trend.hashed == old_trend.hashed:
                new_trend.delta = old_index - new_index
        new_trends[new_index] = new_trend
    return new_trends


def calculate_trends() -> List[Trend]:
    trends: Dict[str, Trend] = {}
    for engine in ENGINE_BIAS.keys():
        for trend in get_trends_by_engine(engine):
            hashed = trend.hashed
            if hashed in trends.keys():
                t_trend = trends[hashed]
                t_trend.add(trend.score, trend.maxscore)
            else:
                t_trend = trend
            trends[hashed] = t_trend

    for trend1 in list(trends.values()):
        hashed1 = trend1.hashed
        is_contain = False
        for trend2 in trends.values():
            hashed2 = trend2.hashed
            if hashed1 == hashed2:
                continue
            if trend2.keyword in trend1.keyword:
                trend2.add(trend1.score * SIMILARITY_WEIGHT, trend1.maxscore)
                trends[hashed2] = trend2
                is_contain = True
        if is_contain:
            del trends[hashed1]
    return sorted(trends.values(), key=lambda x: x.score, reverse=True)


def update_top_articles(trends: List[Trend]):
    for index, trend in enumerate(trends):
        url = (
            "https://search.naver.com/search.naver?where=news&sm=tab_jum&query="
            + parse.quote(trend.keyword)
        )
        req = requests.get(url)
        if req.status_code == 200:
            html = req.text
            soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")
            news = soup.select("ul.list_news > li")
            trends[index].topArticles = []
            topArticles = []
            for new in news:
                title = (
                    new.select_one("a.news_tit").attrs.get("title", "")
                    if new.select_one("a.news_tit")
                    else ""
                )
                links = [
                    link.attrs.get("href", "")
                    for link in new.select("a.info")
                    if link.attrs.get("class", []) == ["info"]
                ]
                link = links[0] if links else ""
                content = (
                    new.select_one("a.api_txt_lines.dsc_txt_wrap").text
                    if new.select_one("a.api_txt_lines.dsc_txt_wrap")
                    else ""
                )
                image = (
                    new.select_one("img.thumb.api_get").attrs.get("src", "")
                    if new.select_one("img.thumb.api_get")
                    else ""
                )
                if title and link and content and image:
                    topArticles.append(Article(title, link, content, image))
                if len(topArticles) >= 3:
                    break
            trends[index].topArticles = topArticles
    return trends


if __name__ == "__main__":
    warnings.filterwarnings(action="ignore")

    print(calculate_trends())
