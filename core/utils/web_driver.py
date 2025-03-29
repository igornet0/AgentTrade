import undetected_chromedriver as uc

class WebDriver(uc.Chrome):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.maximize_window()

class WebOptions(uc.ChromeOptions):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)