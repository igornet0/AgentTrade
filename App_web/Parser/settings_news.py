import time
import requests

class Img:

    def __init__(self, content):
        self.content = content

    def save(self, path):
        with open(path, "wb") as f:
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

def ambcrypto_news(api, newslist: dict[str, str]):
    filter_tags = ["h1", "h2", "p", "em", "span", "img"]

    for text, url in newslist.items():
        driver = api.start_web(url, show_browser=False)
        time.sleep(2)  # Ждем загрузки страницы (можно настроить по необходимости)

        elements = driver.find_elements("tag name", "*")
        flag = False
        text_page = []
        print(text)
        for i, element in enumerate(elements):
            if not element.tag_name in filter_tags:
                if element.tag_name == "a":
                    if "Take a Survey:" in element.text:
                        break
                continue

            t = element.text.strip().replace("\n", "")

            if t:
                # print(i, element.tag_name, t)
                if t == text:
                    flag = True
                    continue

                elif "Read" in t or "Source:" in t:
                    continue

                elif "'Disclaimer:" in t:
                    break

            elif flag and element.tag_name == "img":
                img_src = element.get_attribute("src")  # Получаем значение атрибута src
                try:
                    # Загружаем изображение
                    response = requests.get(img_src)            
                    if response.status_code == 200:  # Проверяем успешность запроса
                        t = Img(response.content)
                    else:
                        continue

                except Exception as e:
                    # print(f"Error loading image: {e}")]
                    continue

            else:
                continue

            if flag:
                if t not in text_page:
                    text_page.append(t)
                    print(t, end=" ")
        # print(text, text_page)
        break
