
from selenium.webdriver.common.by import By
import pandas as pd

from .Api import Parser_api
import time, os, requests, threading, re
from datetime import datetime

from .settings_news import URL_SETTINGS, Img, PATH_DATASET


class Parser_news(Parser_api):

    def __init__(self, urls: list, tick: int = 1, save: bool = False, path_save: str="datasets_news", DEBUG: bool = False) -> None:

        super().__init__(tick=tick, save=save, path_save=path_save, DEBUG=DEBUG, xpath_default=[])

        self.urls = urls
        self.setting = None

    def start_web(self, URL = None, show_browser = True, window_size = ...):
        result = super().start_web(URL, show_browser, window_size)
        
        lfk = threading.Thread(target=self.device.kb.create_lfk, args=("s", "[INFO] For start press '{}'"), daemon=True,)
        lfk.start()
        
        return result

    def load_settings(self, url: str):
        self.setting = URL_SETTINGS.get(url)
        return self.setting
    
    def clear_text(self, text: str):
        cleaned = re.sub(r'b[A-Z]+s+d+s+[A-Z]+b', '', text)
        # Удаляем лишние пробелы
        cleaned = cleaned.strip()

        return cleaned
    
    def url_getter(self, data: list,  urls = {}) -> dict[str, str]:
        for link in data:
            text = link.text.strip()
            url = link.get_attribute("href")
            if text:
                if len(text) > 30:
                    if self.setting.get("clear", False):
                        text = self.clear_text(text)
                    print(text)
                    urls[text] = url
        
        return urls
    

    def parser_elements(self, title):

        setting_news = self.setting.get("news")

        filter_tags: list[str] = setting_news.get("filter_tags", [])
        text_start: str = setting_news.get("text_start") 
        text_end: list[str] = setting_news.get("text_end")
        tag_end: dict[str, str] = {tag.split("//")[-1]: tag.split("//")[0] for tag in setting_news.get("tag_end")}
        text_continue: list[str] = setting_news.get("text_continue")
        img_continue: list[str] = setting_news.get("img_continue")
        date_format: str = setting_news.get("date_format")

        flag = False
        date = None
        text_page = []
        imgs = []
        n = 1
        elements = self.get(tag="*")

        for element in elements:
            if not element.tag_name in filter_tags or element.tag_name in tag_end.values():
                text = element.text.strip().replace("\n", "").lower()
                if text and tag_end.get(text, False):
                    break

                continue

            if flag and element.tag_name == "img":
                alt = element.get_attribute("alt").lower()

                if any(alt.startswith(x.lower()) for x in img_continue):
                    continue

                img_src = element.get_attribute("src")
                try:
                    text = f"IMG_{n}"
                    response = requests.get(img_src)     
                    path_file = f"{len(os.listdir(os.path.join(PATH_DATASET, 'images'))) + 1}.png"
                    Img(response.content).save(path_file)
                    imgs.append(path_file)  
                    n += 1

                except Exception as e:
                    # print(f"Error loading image: {e}")
                    continue
            
            else:
                text = element.text.strip().replace("\n", "").lower()

            if text:
                if text_start == "title":
                    if title.lower().startswith(text):
                        flag = True
                        continue
                else:
                    if any(text.startswith(x.lower()) for x in text_start):
                        flag = True
                        continue

                if any(text.startswith(x.lower()) for x in text_continue):
                    continue

                elif any(text.endswith(x.lower()) for x in text_end):
                    break

                elif date is None:
                    try:
                        date = datetime.strptime(text, date_format)
                    except Exception as e:
                        pass
                
                if flag:
                    if not text in text_page:
                        text_page.append(text)

        return date, text_page, imgs
    
    def captcha_solver(self):
        while True:
            if self.device.kb.get_loop():
                break
        return True
            
    
    def start_parser(self, counter_news=1) -> pd.DataFrame:
        data = pd.DataFrame(columns=["datetime", "url", "title", "text", "imgs"])

        for url in self.urls:
            if not self.load_settings(url):
                continue
            
            self.start_web(url, show_browser=self.setting.get("CAPTHA", False))

            if self.setting.get("CAPTHA", False):
                self.captcha_solver()
            
            news_urls = self.url_getter(self.get())

            if self.setting.get("next_page"):
                for _ in range(counter_news):
                    element = self.search_element(self.get(), self.setting.get("next_page"))
                    self.click(element)
                    time.sleep(2)
                    news_urls = self.url_getter(self.get(), news_urls)
            
            print(f"[INFO parser] {url} {len(news_urls)=}")

            settings_news = self.setting.get("news")
            if not settings_news:
                data = pd.DataFrame(columns=[ "url", "title"])
            
            self.driver.quit()
            self.driver = None

            for title, url_news in news_urls.items():
                if not settings_news:
                    data.loc[len(data)] = [url_news, title]
                    continue
                    
                if title in data["title"].values:
                    continue

                self.start_web(url_news, show_browser=self.setting.get("CAPTHA", settings_news.get("ZOOM", False)))
                
                if settings_news.get("CAPTHA", False):
                    self.captcha_solver()

                if settings_news.get("ZOOM", False):
                    self.driver.execute_script(f"document.body.style.zoom = '{settings_news.get('ZOOM') * 100}%'")

                if settings_news.get("SHOW", False):
                    scroll = settings_news.get("SCROLL", False)
                    if scroll:
                        for _ in range(abs(scroll//100)):
                            self.device.cursor.scroll(scroll//10)
                            time.sleep(self.tick)

                date, text_page, imgs = self.parser_elements(title)
                data.loc[len(data)] = [date, url_news, title, " ".join(text_page), " ".join(imgs)]
            
        return self.save_data(data) if self.save else data