from dataclasses import dataclass


@dataclass()
class Article:
    title: str
    link: str
    content: str
    thumnail: str
