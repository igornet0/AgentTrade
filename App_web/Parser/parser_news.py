
from selenium.webdriver.common.by import By

from .Api import Parser_api, time


class Parser_news(Parser_api):

    def __init__(self, urls: list, save: bool = False, path_save: str="datasets_news", DEBUG: bool = False) -> None:

        super().__init__(save=save, path_save=path_save, DEBUG=DEBUG, xpath_default=[])

        self.urls = urls

    def start_parser(self) -> None:
        
        for url in self.urls:
            self.start_web(url, show_browser=False)
            time.sleep(2)  # Ждем загрузки страницы (можно настроить по необходимости)

            # Поиск заголовка
            title = self.driver.find_element(By.TAG_NAME, 'h1').text.strip()

            # Поиск даты публикации
            # date_element = self.driver.find_element(By.TAG_NAME, 'time')
            # date = date_element.get_attribute('datetime') or date_element.text.strip()

            # Поиск текста новости
            article = self.driver.find_element(By.CLASS_NAME, 'article-content')  # Нужно подбирать правильный класс
            article_text = article.text.strip() if article else None

            # Поиск изображения
            image = self.driver.find_element(By.TAG_NAME, 'img')  # Обычно основное изображение это тег <img>
            image_url = image.get_attribute('src') if image else None

            return {
                'title': title,
                'article_text': article_text,
                'image_url': image_url,
                'url': url
            }
        
        self.driver.quit()  # Закрываем браузер