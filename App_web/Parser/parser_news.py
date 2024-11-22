
from selenium.webdriver.common.by import By
import pandas as pd

from .Api import Parser_api
import time, os, requests, threading, re
from datetime import datetime

from .settings_news import URL_SETTINGS, Img, PATH_DATASET

from ..Log import Loger


class Parser_news(Parser_api):

    def __init__(self, setting: dict = None, tick: int = 1, save: bool = False, path_save: str="datasets_news", logger: Loger = None) -> None:

        super().__init__(tick=tick, save=save, path_save=path_save, logger=logger, xpath_default=[])

        self.setting = setting

    def load_settings(self, url: str):
        self.setting = URL_SETTINGS.get(url)
        return self.setting
    
    def clear_text(self, text: str):
        cleaned = re.sub(r'b[A-Z]+s+d+s+[A-Z]+b', '', text)
        # Удаляем лишние пробелы
        cleaned = cleaned.strip()

        return cleaned
    
    def click_next_page(self):
        if self.setting.get("next_page"):
            element = self.search_element(self.get(), self.setting.get("next_page"))
            self.click(element)
            time.sleep(2)

            return self.get()
    
    def url_getter(self, data: list, filter_text = lambda x: True, counter=1) -> dict[str, str]:
        
        urls = {}
        for _ in range(counter):
            for link in data:
                text = link.text.strip()
                url = link.get_attribute("href")

                if text and filter_text(text):
                    if self.setting.get("clear", False):
                        text = self.clear_text(text)
                    # print(text)
                    urls[text] = url

            data = self.click_next_page()
            if not data:
                break
        
        return urls
    
    
    def process_img(self, element, setting):
        img_continue: list[str] = setting.get("img_continue")

        if img_continue and any(element.get_attribute(x.split("@")[0]).lower().startswith(x.split("@")[-1].lower()) for x in img_continue):
            return False

        img_src = element.get_attribute("src")

        try:
            response = requests.get(img_src)     
            path_file = f"{len(os.listdir(os.path.join(PATH_DATASET, 'images'))) + 1}.png"
            Img(response.content).save(path_file)
            return path_file

        finally:
            return False


    def parser_elements(self, elements, title, setting):
        
        if setting.get("filter_text", False):
            filter_text = setting.get("filter_text")
        else:
            filter_text = lambda x: True        

        filter_tags: list[str] = setting.get("filter_tags", [])
        text_start: str = setting.get("text_start") 
        text_end: list[str] = setting.get("text_end")
        tag_end: dict[str, str] = {tag.split("//")[-1]: tag.split("//")[0] for tag in setting.get("tag_end")}
        text_continue: list[str] = setting.get("text_continue")
        date_format: str = setting.get("date_format")

        flag = False
        date = None
        text_page = []
        imgs = []

        for element in elements:
            if not element.tag_name in filter_tags or element.tag_name in tag_end.values():
                text = element.text.strip().replace("\n", "").lower()
                if tag_end and text and tag_end.get(text, False):
                    break

                continue

            if flag and element.tag_name == "img":
                path_file = self.process_img(element, setting)

                if path_file:
                    imgs.append(path_file)
                    text = f"IMG_{len(imgs)}"
                else:
                    continue
                
            else:
                text = element.text.strip().replace("\n", "").lower()

            if text:
                if text_start == "title":
                    if title.lower().startswith(text):
                        flag = True
                        continue
                else:
                    if any(x in text for x in text_start):
                        flag = True
                        continue

                if date is None:
                    try:
                        date = datetime.strptime(text, date_format)
                    except Exception as e:
                        pass

                if not flag:
                    continue

                if text_continue and any(x in text for x in text_continue):
                    continue

                elif text_end and any(x in text for x in text_end):
                    break
                
            text_page.append(text)

        return date, text_page, imgs
    
    def captcha_solver(self):
        lfk = threading.Thread(target=self.device.kb.create_lfk, args=("s", "[INFO] For start press '{}'"), daemon=True,)
        lfk.start()

        while True:
            if self.device.kb.get_loop():
                break

        return True
            
    
    def parser_news(self, news_urls:dict[str, str]) -> pd.DataFrame:
        settings_news = self.setting.get("news")

        if not settings_news:
            data = pd.DataFrame(columns=["url", "title"])
        else:
            data = pd.DataFrame(columns=["datetime", "url", "title", "text", "imgs"])

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
                    self.device.cursor.scroll(scroll)

            setting_news = self.setting.get("news")
            
            elements = self.get(tag="*")
            date, text_page, imgs = self.parser_elements(elements, title, setting_news)
            data.loc[len(data)] = [date, url_news, title, " ".join(text_page), " ".join(imgs)]

        return data

    def start_parser(self, url:str, counter_news=1) -> pd.DataFrame:

        if not self.setting:
            self.setting = URL_SETTINGS.get(url)

        if not self.setting:
            raise Exception("Setting not found")
        
        self.load_settings(url)
        
        self.start_web(url, show_browser=self.setting.get("CAPTHA", self.setting.get("SHOW", False)))

        if self.setting.get("CAPTHA", False):
            self.captcha_solver()
        
        if self.setting.get("filter_text", False):
            filter_text = self.setting.get("filter_text")
        else:
            filter_text = lambda x: True    
        
        news_urls = self.url_getter(self.get(), filter_text=filter_text, counter=counter_news)

        if self.logger:
            self.logger["INFO"](f"{url} {len(news_urls)=}")

        data = self.parser_news(news_urls)       
            
        return self.save_data(data) if self.save else data