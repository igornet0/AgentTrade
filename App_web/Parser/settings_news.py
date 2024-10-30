from selenium.webdriver.common.by import By

import time
import requests, os
from datetime import datetime
import pandas as pd

PATH_DATASET = "datasets_news"

class Img:

    def __init__(self, content):
        self.content = content

    def save(self, path):
        with open(os.path.join(PATH_DATASET, "images", path), "wb") as f:
            f.write(self.content)

    def __str__(self):
        return "img"
    

URL_SETTINGS = {
    "https://ambcrypto.com/category/new-news/":{
        "next_page": "load more articles",
        "filter_text": lambda x: len(x) > 26,
        "news": {
            "SHOW": True,
            "SCROLL": -1000,
            "ZOOM": 0.6,
            "text_start": "title",
            "text_end": ["Disclaimer:"],
            "tag_end": ["a//take a survey:"],
            "text_continue": ["2min", "source:"],
            "img_continue": ["alt@avatar"],
            "date_format": "posted: %B %d, %Y",
            "filter_tags": ["h1", "h2", "p", "em", "span", "img"]
            }
        },
    "https://cryptoslate.com/crypto/":{
        "CAPTHA": True,
        "next_page": "next page",
        "filter_text": lambda x: len(x) > 20,
        "clear": True,
        "news": {
            "SHOW": True,
            "SCROLL": -1000,
            "ZOOM": 0.6,
            "text_start": "title",
            "tag_end": ["div//Posted In:"],
            "text_continue": ["2min", "source:"],
            "img_continue": ["data-del@avatar"],
            "date_format": "Updated: %b. %d, %Y at %I:%M %p %Z",
            "filter_tags": ["h1", "h2", "p", "em", "span", "img"]
            }
    }
}