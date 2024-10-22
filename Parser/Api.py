from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

import threading

import pandas as pd
from PIL import Image

import time, base64, random
from io import BytesIO
from datetime import datetime
from shutil import rmtree
from os import mkdir, chdir, listdir, getcwd, path

from .Device import Device
from .datetime_process import *

dict_timetravel = {"1Д":"1D", "4Ч":"4H", "1Ч":"1H", "5 минут":"5m", "15 минут":"15m"}

class Web_api:

    def __init__(self, tick:int = 1, 
                 save:bool = False, path_save="datasets", DEBUG=False, 
                 xpath_default:list = ["login", "password", "click_login", "filename", "timetravel"]) -> None:
        
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

    def default_xpath_bcs(self):
        self.add_xpath("login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div/div/input")
        #self.add_xpath("password", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[2]/div/div/input")
        self.add_xpath("click_login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[3]/button[1]")
        self.add_xpath("frame", "/html/body/div[1]/div[3]/div[3]/div[2]/div/div/div[3]/div/div[1]/div[2]/div/div/div[2]/div/div/div[2]/iframe")
        self.add_xpath("filename", "/html/body/div[1]/div[3]/div[3]/div[2]/div/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div[2]/label[1]/span/div/span")
        self.add_xpath("timetravel", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[1]/div/div[1]/div[1]/div[3]")
        self.add_xpath("datetime", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[4]/td[2]/div/canvas[2]")
        self.add_xpath("open", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[1]/div/div[2]/div/div[2]/div[2]")
        self.add_xpath("max",  "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[1]/div/div[2]/div/div[3]/div[2]")
        self.add_xpath("min", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[1]/div/div[2]/div/div[4]/div[2]")
        self.add_xpath("close", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[1]/div/div[2]/div/div[5]/div[2]")
        self.add_xpath("volume", "/html/body/div[2]/div[3]/div/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]/div")
        
        if self.xpath_vxod.keys() != self.xpath_defaul_vxod:
            raise ValueError(f"XPATH not found {self.xpath_vxod.keys() - self.xpath_defaul_vxod}")

    def default_xpath_kucoin(self):
        # self.add_xpath("login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div/div/input")
        # self.add_xpath("password", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[2]/div/div/input")
        # self.add_xpath("click_login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[3]/button[1]")
        self.add_xpath("filename", "//h1[contains(@class,'lrtcss-c7k6qm')]", default=True)
        self.add_xpath("timetravel", "//div[contains(@class,'dropdown-value lrtcss-1qeuv02')]", default=True)

        self.add_xpath("frame", "iframe")
        self.add_xpath("datetime", "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[4]/td[2]/div/canvas[2]")
        self.add_xpath("open", "//div[2]/div[2]")
        self.add_xpath("max",  "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div/div/div[2]/div/div[3]/div[2]")
        self.add_xpath("min", "//div[4]/div[2]")
        self.add_xpath("close", "//div[5]/div[2]")
        self.add_xpath("volume", "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[3]/td[2]/div/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div")

        if self.xpath_vxod.keys() - self.xpath_defaul_vxod:
            raise ValueError(f"XPATH not found {self.xpath_vxod.keys() - self.xpath_defaul_vxod}")
        
    def start_web(self, URL:str = None, entry: bool = True, 
                  login: str = None, password: str = None,
                  window_size: tuple = (1100, 1000)):
        
        if "bcs" in URL:
            self.default_xpath_bcs()
        elif "kucoin" in URL:
            self.default_xpath_kucoin()

        self.driver.set_window_size(*window_size)
        self.driver.get(URL) 
        self.driver.switch_to.default_content()

        self.URL = URL
        self.login = login
        self.password = password

        keypress_thread = threading.Thread(target=self.device.kb.listen_for_keypress, daemon=True)
        keypress_thread.start()

        pause_thread = threading.Thread(target=self.device.kb.pause, daemon=True)
        pause_thread.start()

        if entry:
            self.entry()

    def end_web(self):
        self.driver.close()

    def restart(self, entry: bool = True):
        self.end_web()
        self.start_web(self.URL, self.login, self.login, entry=entry)

    def entry(self):
        if self.DEBUG:
            input("Chekpoint #1")

        self.get_element(self.xpath_vxod["login"])[0].send_keys(self.login)
        self.get_element(self.xpath_vxod["password"])[0].send_keys(self.password)
        self.get_element(self.xpath_vxod["click_login"])[0].click()

        return True

    def switch_frame(self):
        frame = self.get_element(self.xpath_vxod["frame"], by=By.TAG_NAME)
        self.driver.switch_to.frame(frame) 
        return True
    
    def add_xpath(self, key:str, xpath:str, default: bool = False):
        if key in self.xpath_defaul_vxod:
            self.xpath_vxod[key] = xpath
        elif default:
            return None
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
    
    def get_element(self, xpath:str, by=By.XPATH, text=False):
        iter = 20
        while True:
            try:
                element = self.driver.find_element(by, xpath)
                if element is None:
                    raise ValueError(f"element {xpath} is None")

                if text:
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

    def get_timetravel(self, default: str = "timetravel") -> str:
        if "timetravel" not in self.xpath_vxod.keys():
            return default
        
        timetravel = self.get_element(self.xpath_vxod["timetravel"], text=True)
        if not timetravel:
            return default
         
        return dict_timetravel[timetravel] if not timetravel.isdigit() else timetravel + "m"

    def get_filename(self, default: str = "data") -> str:
        if not self.file is None:
            return self.file

        if "filename" not in self.xpath_vxod.keys():
            filename = default
        else:
            filename = self.get_element(self.xpath_vxod["filename"], text=True)
            if not filename:
                return None

        self.file = f"{filename}-{self.get_timetravel()}.csv" 
        self.file = self.file.replace("/", "_")

        return self.file

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
        
        datetime_last = data['datetime'].min().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO parser] Last datetime = {datetime_last}")
        print(f"[INFO parser] End parser")

        return (datetime_last, self.save_data(data)) if self.save else (datetime_last, data)

    def start_parser(self, datetime_last: datetime = None, counter: int = 1) -> pd.DataFrame:
        self.wait_element(self.xpath_vxod["frame"])

        self.device.cursor.set_position()
        self.device.cursor.move_to_position()
        
        data = pd.DataFrame(columns=self.xpath.keys())
        self.get_filename()

        status = self.switch_frame()
        if not status:
            raise ValueError("Frame not found")
        
        self.device.cursor.click()
        
        if not datetime_last is None:
            if not self.search_datetime(datetime_last):
                raise ValueError("Datetime not found")
            datetime_last = None

        print(f"[INFO parser] Start parser")

        time_start = time.time()
        for _ in range(counter):
            if self.device.cursor.get_position_now() != self.device.cursor.get_position["start"]:
                self.device.cursor.move_to_position()

            data_d = self.get_elements()

            if data_d:
                if datetime_last is None:
                    datetime_last = data_d["datetime"]

                elif data_d['datetime'] >= datetime_last:
                    while data_d and data_d['datetime'] > data['datetime'].min():
                        self.device.kb.hotkey("left", interval=random.randint(1, 3))
                        data_d = self.get_elements()
                    
                    datetime_last = data["datetime"].min()

                if data_d:
                    data.loc[len(data)] = data_d

                    if len(data) % (counter // 10) == 0:
                        time_end = time.time()
                        print(f"[INFO parser] {len(data)}/{counter} {round((time_end - time_start) / 60, 2)} min")
                        time_start = time.time()

            self.device.cursor.move("right")

            if self.device.kb.get_stop_loop():
                print(f"[INFO parser] Stop parser by keypress")
                break

            time.sleep(self.tick)

        return self.finally_parser(data, counter)
        
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

    def parser_for_df(self, df: pd.DataFrame):
        self.wait_element(self.xpath_vxod["frame"])

        if self.device.cursor.get_position["start"] is None:
            self.device.cursor.set_position()

        self.get_filename()

        data = pd.DataFrame(columns=self.xpath.keys())
        temp_print_col_nan = 0
        temp_colnan = 0
        df = df.sort_values('datetime', ignore_index=True, ascending=False)
        
        status = self.switch_frame()
        if not status:
            raise ValueError("Frame not found")
        print(f"[INFO parser] Start parser {len(df)}")
        try:
            for date in df["datetime"]:
                if self.search_datetime(date):
                    data_d = self.get_elements()
                    if data_d["datetime"] != date:
                        print("[ERROR] Datetime not match!")
                        continue

                    data.loc[len(data)] = data_d
                    temp_colnan += 1
                else:
                    print(date, " -Not Found!")

                temp_print_col_nan += 1
                if temp_print_col_nan == 10:
                    col_nan = len(df) - temp_colnan
                    print(f"[INFO] {col_nan=}")
                    temp_print_col_nan = 0

                if not self.handler_loop():
                    break

            data["datetime"] = pd.to_datetime(data['datetime'])

        except Exception as e:
            print("[ERROR parser_for_df] ", e)
        
        finally:
            return self.finally_parser(data, len(df))

    def save_data(self, data):
        self.create_launch_dir()
        data.to_csv(path.join(self.path, self.file), index=False)
        return data
    
    def create_launch_dir(self) -> None:
        if self.path not in listdir(self.main_dir):
            mkdir(self.path)

        n = len([f for f in listdir(self.path) if f.startswith("launch")]) + 1

        self.path = path.join(self.path, f"launch_{n}")
        mkdir(self.path)

    def remove_launch_dir(self):
        chdir(self.main_dir)
        rmtree(self.path_save)

    def __del__(self):
        self.end_web()
