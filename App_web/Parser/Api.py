from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import threading

import pandas as pd
from PIL import Image

import time, base64, json
from io import BytesIO
from datetime import datetime
from shutil import rmtree
from os import mkdir, chdir, listdir, getcwd, path

from .Device import Device
from .datetime_process import *

from .settings_news import *

class Parser_api:

    def __init__(self, tick:int = 1, 
                 save:bool = False, path_save="datasets", DEBUG=False, 
                 xpath_default:list = ["login", "password", "click_login", "frame", "filename", "timetravel"]) -> None:

        self.driver = None

        self.save = save
        self.file = None
        self.path_trach = None
        self.path_save = path_save
        self.main_dir = getcwd()

        self.tick = tick

        self.xpath = {}
        self.xpath_vxod = {}

        self.device = Device(tick=self.tick)
        self.buffer_date = []

        self.DEBUG = DEBUG

        self.xpath_defaul_vxod = xpath_default

        self.keypress_thread = threading.Thread(target=self.device.kb.listen_for_keypress, daemon=True)
        self.keypress_thread.start()

        self.pause_thread = threading.Thread(target=self.device.kb.pause, daemon=True)
        self.pause_thread.start()


    def start_web(self, URL:str = None, show_browser: bool = True, window_size: tuple = (1100, 1000)):
        if self.driver is None:
            options = uc.ChromeOptions() 

            if not show_browser:
                options.add_argument("--headless")

            self.driver = uc.Chrome(options=options, use_subprocess=True)

        self.driver.get(URL) 
        time.sleep(3)

        self.driver.switch_to.default_content()

        self.URL = URL

        return self.driver

    def end_web(self):
        self.driver.quit()

    def restart(self):
        self.end_web()
        self.start_web(self.URL)
    
    def switch_frame(self):
        frame = self.get_element(self.xpath_vxod["frame"], by=By.TAG_NAME)
        self.driver.switch_to.frame(frame) 
        return True
    
    def get(self, by=By.TAG_NAME, tag="a") -> list:
        return self.driver.find_elements(by, tag)

    def click(self, element):
        element.click()
        time.sleep(2)

    def search_element(self, elements, text):
        for element in elements:
            if text and text in element.text.strip().replace("\n", "").lower():
                return element
            
        return False
    
    def add_xpath(self, key:str, xpath:str):
        if key in self.xpath_defaul_vxod:
            self.xpath_vxod[key] = xpath
        else:
            self.xpath[key] = xpath

    def get_elements(self) -> dict:
        data_d = {}
        for key, xpath in self.xpath.items():
            if key == "datetime":
                element = self.get_element_datetime()
                if element is None:
                    return False
            else:
                element = self.get_element(xpath, text=True)
                
            data_d[key] = element

        return data_d

    
    
    def get_element(self, xpath:str, by=By.XPATH, text=False, all=False):
        iter = 20
        while True:
            try:
                if all:
                    element = self.driver.find_elements(by, xpath)
                else:
                    element = self.driver.find_element(by, xpath)

                if element is None:
                    raise ValueError(f"element {xpath} is None")

                if text:
                    if all:
                        return [e.text if e.text else "" for e in element]
                    
                    if not element.text:
                        continue

                    return element.text
                
                return element
            
            except Exception as e:
                iter -= 1
                time.sleep(self.tick)
                if iter == 0:
                    print(f"[ERROR get_element] {e}")
                    break

    def set_filename(self, filename: str):
        self.file = filename

    def wait_element(self, xpath:str) -> bool:
        while self.get_element(xpath, by=By.TAG_NAME) is None:
            time.sleep(self.tick)

        return True
    
    def finally_parser(self, data: pd.DataFrame, counter: int = 1):
        if len(data) != counter:
                print(f"[INFO parser] {len(data)}/{counter}")
            
        if len(data) == 0:
            return (None, None)
        
        datetime_last = data['datetime'].min()
        print(f"[INFO parser] Last datetime = {datetime_last}")
        print(f"[INFO parser] End parser")

        return (datetime_last, self.save_data(data)) if self.save else (datetime_last, data)

    def get_element_datetime(self):
        error_buffer = []
        while True:
            element = self.get_element(self.xpath["datetime"])
            date, img = self.get_datatime(element)

            if date:
                return date
            else:
                error_buffer.append(date)
                if len(error_buffer) > 10:
                    if not self.path_trach is None:
                        img.save(path.join(self.path_trach, f"{len(listdir(self.path_trach)) + 1}_error.png"))
                    print(f"[ERROR get_element_datetime] {error_buffer[-1]}")
                    return False
                
    def get_img(self, element):
        image_data = base64.b64decode(self.driver.execute_script('return arguments[0].toDataURL().substring(21);', element))
        img = Image.open(BytesIO(image_data))
        return img

    def get_datatime(self, element):
        img = self.get_img(element)
        try:
            text = image_to_text(img)
            date = str_to_datatime(text)
            return date, img
        except Exception:
            return False, img
        

    def handler_loop(self):
        if self.device.kb.get_stop_loop():
            print(f"[INFO parser] Stop parser by keypress")
            return False
            
        if self.device.kb.get_pause_loop():
            print(f"[INFO parser] Pause parser by keypress")
            while self.device.kb.get_pause_loop():
                time.sleep(5)
            return True
        
        return True

    def search_datetime(self, target_datetime: datetime, right_break: bool = False, ) -> bool:
        buffer_life = 3

        print(f"[INFO search_datetime] start search {target_datetime}")
        self.device.cursor.scroll_to_start()
        while True:

            if not self.handler_loop():
                return False
            
            date = self.get_element_datetime() or self.get_last_buffer_date()

            if date is None:
                continue

            self.buffer_date.append(date)

            delta = abs((target_datetime - date).total_seconds())

            if delta == 0:
                print(f"[INFO search_datetime] datetime {target_datetime} found")
                self.buffer_date = []
                return True
            
            if self.should_clear_buffer():
                date = self.buffer_date[-1]
                buffer_life -= 1
                print("[INFO search_datetime] clear buffer")
                if buffer_life == 0:
                    self.device.cursor.scroll(-25)
                    print(f"[INFO search_datetime] datetime {target_datetime} not found")
                    print(f"[INFO search_datetime] {self.buffer_date=}")
                    return False
                
                self.buffer_date = []
                self.device.cursor.scroll(25)
            
            direction = self.determine_direction(target_datetime, date)
            if direction == "right" and right_break:
                break
            
            interval = self.determine_interval(delta)
            self.device.cursor.move(direction + interval)
            self.device.cursor.move_to_position()

    def get_last_buffer_date(self):
        return self.buffer_date[-1] if self.buffer_date else None

    def should_clear_buffer(self):
        if len(self.buffer_date) > 10:
            if len(set(self.buffer_date)) <= 5:
                return True
        return False

    def determine_direction(self, target_datetime, date):
        if target_datetime < date:
            return "left"
        else:
            return "right"

    def determine_interval(self, delta):
        if delta / 60 < 60 * 4:
            return ""
        if delta / 60 < 60 * 8:
            return "_middle"
        else:
            return "_fast"
        
    def set_save_trach(self, path:str):
        self.path_trach = path

    def save_data(self, data):
        self.create_launch_dir()
        data.to_csv(path.join(self.path_save, self.file), index=False)
        return data
    
    def create_launch_dir(self) -> None:
        if self.path_save not in listdir(self.main_dir):
            mkdir(self.path_save)

        n = len([f for f in listdir(self.path_save) if f.startswith("launch")]) + 1

        self.path_save = path.join(self.path_save, f"launch_{n}")
        mkdir(self.path_save)

    def remove_launch_dir(self):
        chdir(self.main_dir)
        rmtree(self.path_save)

    def rec_xpath(self, url):
        self.start_web(url)    

        xpath = {}

        # Функция для получения XPath элемента
        self.driver.execute_script("""
            let xpathList = [];
            let classNamesList = [];
                                   
            document.addEventListener('click', function(event) {
                event.preventDefault();
                let element = event.target;
                let xpath = '';
                let currentNode = element;

                // Получаем название классов
                let classNames = Array.from(element.classList).join(' ');

                while (currentNode) {
                    let name = currentNode.localName;
                    let index = Array.from(currentNode.parentNode ? currentNode.parentNode.children : []).indexOf(currentNode) + 1;
                    xpath = '/' + name + '[' + index + ']' + xpath;
                    currentNode = currentNode.parentNode;
                }

                xpathList.push(xpath);
                classNamesList.push(classNames);
                console.log('XPath:', xpath);  // Выводим XPath в консоль
                console.log('Class Names:', classNames);  // Выводим названия классов в консоль
            });

            window.getXpathList = function() { return xpathList; };  // Функция для получения списка
            window.getclassNamesList = function() { return classNamesList; };
        """)

        print(f"[INFO rec_xpath] Start rec xpath")
        while True:
            time.sleep(0.5)

            [xpath.setdefault(c, set()).add(x) for x, c in zip(self.driver.execute_script("return getXpathList()"), self.driver.execute_script("return getclassNamesList()"))]

            if not self.handler_loop():
                break

        print(f"[INFO rec_xpath] End rec xpath")
        print(xpath)

        for key, value in xpath.items():
            xpath[key] = list(value)

        with open("xpath_rec.json", "w") as f:
            json.dump(xpath, f)



    def __del__(self):
        if self.driver is None:
            return
        
        self.end_web()
