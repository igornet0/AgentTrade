from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import threading

import pandas as pd
from PIL import Image

import time, base64
from io import BytesIO
from datetime import datetime
from shutil import rmtree
from os import mkdir, chdir, listdir, getcwd, path

from .Device import Device
from .datetime_process import *

class Parser_api:

    def __init__(self, tick:int = 1, 
                 save:bool = False, path_save="datasets", DEBUG=False, 
                 xpath_default:list = ["login", "password", "click_login", "frame", "filename", "timetravel"]) -> None:
        
        options = uc.ChromeOptions() 
        self.driver = uc.Chrome(use_subprocess=True, options=options) 

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


    def start_web(self, URL:str = None, window_size: tuple = (1100, 1000)):

        self.driver.set_window_size(*window_size)
        self.driver.get(URL) 
        self.driver.switch_to.default_content()

        self.URL = URL

        keypress_thread = threading.Thread(target=self.device.kb.listen_for_keypress, daemon=True)
        keypress_thread.start()

        pause_thread = threading.Thread(target=self.device.kb.pause, daemon=True)
        pause_thread.start()

    def end_web(self):
        self.driver.close()

    def restart(self):
        self.end_web()
        self.start_web(self.URL)
    
    def switch_frame(self):
        frame = self.get_element(self.xpath_vxod["frame"], by=By.TAG_NAME)
        self.driver.switch_to.frame(frame) 
        return True
    
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

    def set_save_trach(self, path:str):
        self.path_trach = path
    
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
            try:
                element = self.get_element(self.xpath["datetime"])
                image_data = base64.b64decode(self.driver.execute_script('return arguments[0].toDataURL().substring(21);', element))

                img = Image.open(BytesIO(image_data))
                text = image_to_text(img)
                date = str_to_datatime(text)
                return date

            except Exception as e:
                error_buffer.append(e)
                if len(error_buffer) == 5:
                    if not self.path_trach is None:
                        img.save(path.join(self.path_trach, f"{len(listdir(self.path_trach)) + 1}_error.png"))
                    print(f"[ERROR get_element_datetime] {error_buffer[-1]}")
                    return False
                time.sleep(2)

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

    def __del__(self):
        self.end_web()
