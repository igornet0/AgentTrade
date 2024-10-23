from .Api import Parser_api

class Parser_news(Parser_api):

    def __init__(self, urls: list, save: bool = False, path_save: str="datasets_news", DEBUG: bool = False) -> None:

        super().__init__(save=save, path_save=path_save, DEBUG=DEBUG, xpath_default=[])

        self.urls = urls

    def start(self) -> None:

        for url in self.urls:
            self.start_web(url, show_browser=False)
            

