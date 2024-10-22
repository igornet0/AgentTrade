from .Api import Parser_api
import pandas as pd
import time
from datetime import datetime
import random

RU_EN_timetravel = {"1Д":"1D", "4Ч":"4H", "1Ч":"1H", "5 минут":"5m", "15 минут":"15m"}
timetravel_int = {"1D":24*3600, "4H":4*3600, "1H":1*3600, "5m":5*60, "15m":15*60}

class Parser_kucoin(Parser_api):

    def __init__(self, tick = 1, save = False, path_save="datasets", DEBUG=False, 
                 xpath_default=["login", "password", "click_login", "frame", "filename", "timetravel"]):
        
        super().__init__(tick, save, path_save, DEBUG, xpath_default)

        self.login = None
        self.password = None

        self.timetravel = None

    
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


    def entry(self, login: str, password: str):
        self.login_xpath()

        self.login = login
        self.password = password

        self.get_element(self.xpath_vxod["login"])[0].send_keys(login)
        self.get_element(self.xpath_vxod["password"])[0].send_keys(password)
        self.get_element(self.xpath_vxod["click_login"])[0].click()

        return True
    
    def start(self):
        self.wait_element(self.xpath_vxod["frame"])

        if self.device.cursor.get_position["start"] is None:
            self.device.cursor.set_position()

        self.device.cursor.move_to_position()

        self.get_filename()

        status = self.switch_frame()
        if not status:
            raise ValueError("Frame not found")
    
    def parser_missing_data(self, df: pd.DataFrame):
        self.start()

        data = pd.DataFrame(columns=self.xpath.keys())
        temp_print_col_nan = 0
        temp_colnan = 0

        df = df.sort_values('datetime', ignore_index=True, ascending=False)
        
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
        
    def paser_fast(self, datetime_last: datetime = None, counter: int = 1) -> pd.DataFrame:
        self.start()

        data = pd.DataFrame(columns=self.xpath.keys())
        
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
    
    def get_timetravel(self, default: str = "timetravel") -> str:
        if not self.timetravel is None:
            return self.timetravel
        
        if "timetravel" not in self.xpath_vxod.keys():
            timetravel = default
        else:
        
            timetravel = self.get_element(self.xpath_vxod["timetravel"], text=True)
        
            if not timetravel:
                timetravel = default
            else:
                timetravel = RU_EN_timetravel[timetravel] if not timetravel.isdigit() else timetravel + "m"
        
        self.set_timetravel(timetravel)
        return timetravel
    
    def set_timetravel(self, timetravel: str):
        self.timetravel = timetravel

    def remove_timetravel(self, timetravel_page: str, timetravel: str = "5m"):
        self.driver.switch_to.default_content()
        print(f"[INFO parser] {timetravel_page} != {timetravel}")
        print(f"[INFO parser] Replace timetravel to {timetravel}")
        for i in range(5):
            print(f"[INFO parser] {i}/5 sec")
            timetravel = self.get_timetravel()
            if timetravel == timetravel_page:
                print(f"[INFO parser] {timetravel} == {timetravel_page}")
                break

            time.sleep(1.3)
    
    def parser(self, datetime_start: datetime = None, counter: int = 1, timetravel: str = "5m") -> pd.DataFrame:
        self.start()

        timetravel_page = self.get_timetravel()

        if timetravel_page != timetravel:
            self.remove_timetravel(timetravel_page, timetravel)
            self.switch_frame()

        data = pd.DataFrame(columns=self.xpath.keys())
        
        self.device.cursor.click()
        
        if not datetime_start is None:
            if not self.search_datetime(datetime_start):
                raise ValueError("Datetime not found")
            datetime_start = None

        print(f"[INFO parser] Start parser")

        time_start = time.time()
        for _ in range(counter):
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


    def restart(self):
        super().restart()
        if self.login:
            self.entry(self.login, self.password)

    

    def login_xpath(self):
        self.add_xpath("login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div/div/input")
        self.add_xpath("password", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[2]/div/div/input")
        self.add_xpath("click_login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[3]/button[1]")


    def default_xpath_kucoin(self):
        self.add_xpath("filename", "//h1[contains(@class,'lrtcss-c7k6qm')]")
        self.add_xpath("timetravel", "//div[contains(@class,'dropdown-value lrtcss-1qeuv02')]")

        self.add_xpath("frame", "iframe")
        self.add_xpath("datetime", "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[4]/td[2]/div/canvas[2]")
        self.add_xpath("open", "//div[2]/div[2]")
        self.add_xpath("max",  "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div/div/div[2]/div/div[3]/div[2]")
        self.add_xpath("min", "//div[4]/div[2]")
        self.add_xpath("close", "//div[5]/div[2]")
        self.add_xpath("volume", "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[3]/td[2]/div/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div")