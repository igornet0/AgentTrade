import time
import requests, os
from datetime import datetime
import pandas as pd

RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

EN_MONTH_VALUES = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}

PATH_DATASET = "datasets_news"

class Img:

    def __init__(self, content):
        self.content = content

    def save(self, path):
        with open(os.path.join(PATH_DATASET, "images", path), "wb") as f:
            f.write(self.content)

    def __str__(self):
        return "img"


def ambcrypto_newslist(api, counter_news=1):
    URL = "https://ambcrypto.com/category/new-news/"
    
    driver = api.start_web(URL, show_browser=False)

    links = driver.find_elements("tag name", "a")

    def load_news():
        for link in links:
            text = link.text.strip()
            if text == "Load More Articles":
                for _ in range(counter_news):
                    link.click()
                    time.sleep(2)
                break   

    load_news()

    links = driver.find_elements("tag name", "a")   
    news = {}
    for link in links:
        text = link.text.strip()
        url = link.get_attribute("href")
        if text:
            if len(text) > 30:
                news[text] = url
    
    driver.quit()

    return news

def ambcrypto_news(api, newslist: dict[str, str]) -> pd.DataFrame:
    filter_tags = ["h1", "h2", "p", "em", "span", "img"]

    if f"{datetime.now().strftime('%Y-%m-%d')}_news.csv" in os.listdir(PATH_DATASET):
        data = pd.read_csv(os.path.join(PATH_DATASET, f"{datetime.now().strftime('%Y-%m-%d')}_news.csv"))
    else:
        data = pd.DataFrame(columns=["datetime", "url", "title", "text", "imgs"])

    for title, url in newslist.items():
        if title in data["title"].values:
            continue

        driver = api.start_web(url, show_browser=True)
        time.sleep(3)
        api.device.cursor.scroll(-800)

        elements = driver.find_elements("tag name", "*")
        flag = False
        date = None

        text_page = []
        imgs = []
        n = 1

        for element in elements:
            if not element.tag_name in filter_tags:
                if element.tag_name == "a":
                    if "Take a Survey:" in element.text:
                        break
                continue
            
            t = element.text.strip().replace("\n", "")

            if t:
                if t == title:
                    flag = True
                    continue

                elif "Read" in t or "Source:" in t:
                    continue

                elif "Posted:" in t:
                    t = t.lower()

                    date = datetime.strptime(t, "posted: %B %d, %Y")
                    continue

                elif "'Disclaimer:" in t:
                    break

            elif flag and element.tag_name == "img":
                alt = element.get_attribute("alt")
                if alt == "Avatar":
                    continue
                img_src = element.get_attribute("src")
                try:
                    # Загружаем изображение
                    t = f"IMG_{n}"
                    response = requests.get(img_src)     
                    path_file = f"{len(os.listdir(os.path.join(PATH_DATASET, 'images'))) + 1}.png"
                    Img(response.content).save(path_file)
                    imgs.append(path_file)  
                    n += 1

                except Exception as e:
                    print(f"Error loading image: {e}")
                    continue
            
            else:
                continue

            if flag:
                if t not in text_page:
                    text_page.append(t)

        if not api.handler_loop():
            break

        data.loc[len(data)] = [date, url, title, " ".join(text_page), " ".join(imgs)]

    data.to_csv(os.path.join(PATH_DATASET, f"{datetime.now().strftime('%Y-%m-%d')}_news.csv"), index=False)

def cryptoslate_news(api, newslist: dict[str, str]) -> pd.DataFrame:
    pass