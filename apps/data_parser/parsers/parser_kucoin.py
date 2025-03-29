import asyncio
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Generator
from fastapi import UploadFile

from apps.data_parser import ParserApi
from apps.data_processing import DatasetTimeseries
from core.utils.decoraters import ui_method
from core.utils.tesseract_img_text import RU_EN_timetravel, timetravel_seconds_int
import logging 

logger = logging.getLogger("parser_logger.ParserKucoin")

class ParserKucoin(ParserApi):

    def __init__(self, tick: int = 1, driver = None, 
                 save: bool = False, timetravel: str = None) -> None:
        
        import_device: bool = True
        super().__init__(tick=tick, driver=driver, save=save, import_device=import_device)

        self.login = None
        self.password = None

        self.timetravel = timetravel

        self.default_xpath()
    
    def get_filename(self, default: str = "data") -> str:
        # if not self.filename is None:
        #     return self.filename

        if "filename" not in self.xpath.keys():
            filename = default
        else:
            filename = self.get_element(self.xpath["filename"]["xpath"], 
                                        text=True, name="filename")
            if not filename:
                 filename = default

        self.filename = f"{filename}-{self.get_timetravel()}.csv" 
        self.filename = self.filename.replace("/", "_")

        logger.debug(f"Get filename {self.filename=}")

        return self.filename
    
    async def test_xpath(self):
        assert self.driver is not None

        data_test = await self.get_elements()

        assert len(data_test) == len(list(filter(lambda x: self.xpath[x]["parse"], self.xpath.keys())))

        if isinstance(data_test["datetime"], Generator):
            data_test["datetime"] = next(data_test["datetime"])
        
        for key, value in data_test.items():
            if not value:
                raise ValueError(f"Xpath not found {key}")

        return True

    async def init(self):
        self.wait_for_page_load()

        if self.device.cursor.get_position["start"] is None:
            self.device.cursor.set_position()

        self.get_filename()

        status = await self.switch_frame()
        status_test = await self.test_xpath()

        self.device.cursor.move_to_position()

        logger.info(f"Init {status=} {status_test=}")

        if not status:
            raise ValueError("Frame not found")
    
    @ui_method(description="Parsing missing date", file_params={
                'file': {
                    'extensions': ['.csv', '.xlsx'],
                    'description': 'CSV или Excel файл'
                }
            })
    async def parser_missing_data(self, df_missing: UploadFile, check_interval: int = 0) -> pd.DataFrame:

        await self.init()

        check_interval = check_interval * timetravel_seconds_int[self.get_timetravel()]

        data = pd.DataFrame(columns=self.xpath.keys())
        temp_print_col_nan = 0
        temp_colnan = 0

        if isinstance(df_missing, str):
            df_missing = DatasetTimeseries(df_missing).get_dataset_Nan()

        df = df_missing.sort_values('datetime', ignore_index=True, ascending=False)
        
        logger.info(f"Start parser {len(df)}")

        try:
            for date in df["datetime"]:
                if check_interval:
                    date = date + timedelta(seconds=check_interval)
                else:
                    check_interval = timetravel_seconds_int[self.get_timetravel()]

                while check_interval != 0:
                    if not await self.search_datetime(date):
                        logger.error(f"{date} -Not Found!")

                    data_d = await self.get_elements()
                    data_d["datetime"] = next(data_d["datetime"])

                    if data_d["datetime"] != date:
                        logger.error(f"Datetime not match! {data_d['datetime']} != {date}")
                    else:
                        self.add_data_buffer(data_d)

                    check_interval -= timetravel_seconds_int[self.get_timetravel()]
                    date = date - timedelta(seconds=timetravel_seconds_int[self.get_timetravel()])

                temp_print_col_nan += 1
                if temp_print_col_nan == 10:
                    col_nan = len(df) - temp_colnan
                    logger.debug(f"{col_nan=}")
                    temp_print_col_nan = 0

                if not await self.handler_loop():
                    break

        except Exception as e:
            logger.error(f"{e}")
        
        finally:
            data["datetime"] = pd.to_datetime(data['datetime'])

            return self.finally_parser(data, len(df))
        
    async def start_parser(self, datetime_last: datetime = None, init_counter: int = 1) -> pd.DataFrame:
        try:
            await self.init()

            self.device.cursor.click()
            
            if not datetime_last is None:
                if not await self.search_datetime(datetime_last):
                    raise ValueError("Datetime not found")
                
                datetime_last = None

            counter = init_counter
            delta = 0
            logger.info(f"Start parser {datetime_last=} {counter=}")

            time_start = time.time()
            while not self.device.kb.stop_event.is_set() and (counter > 0):
                if self.device.cursor.get_position_now() != self.device.cursor.get_position["start"]:
                    self.device.cursor.move_to_position()

                data_d = await self.get_elements()

                if data_d:
                    if datetime_last is None:
                        data_d["datetime"] = next(data_d["datetime"])
                        datetime_last = data_d["datetime"]
                        while datetime_last is None or (life := 3) != 0:
                            data_d = await self.get_elements()
                            data_d["datetime"] = next(data_d["datetime"])
                            datetime_last = data_d["datetime"]
                            life -= 1
                            
                    elif delta <= 0:

                        data_d["datetime"] = next(data_d["datetime"])

                        while data_d["datetime"] is None:
                            data_d = await self.get_elements()
                            data_d["datetime"] = next(data_d["datetime"])
                            datetime_last = data_d["datetime"]

                        while data_d and data_d["datetime"] > datetime_last:
                            self.device.kb.hotkey("option", "left", interval=self.tick)
                            data_d = await self.get_elements()
                            data_d["datetime"] = next(data_d["datetime"])

                        interval = timetravel_seconds_int[self.get_timetravel()] 
                        delta = datetime_last - data_d["datetime"]
                        delta = delta.total_seconds() // interval
                        datetime_last = data_d["datetime"]

                    if data_d:
                        self.add_data_buffer(data_d)

                        if len(self.get_data_buffer()) % 1000 == 0:
                            time_end = time.time()
                            logger.info(f"{len(self.get_data_buffer())}/{init_counter} {round((time_end - time_start) / 60, 2)} min")
                            time_start = time.time()
                        
                        counter -= 1    
                        delta -= 1

                    self.device.cursor.move("right")

                if not await self.handler_loop():
                    break

        except Exception as e:
            logger.error(f"Parser error: {str(e)}")
            self.device.kb.stop_event.set()

        finally:

            for data_d in filter(lambda x: isinstance(x["datetime"], Generator), self.get_data_buffer()):
                data_d["datetime"] = next(data_d["datetime"])

            for i in self.get_data_buffer():
                if None in i.values():
                    logger.debug(f"None in {i}")

            data = pd.DataFrame(self.get_data_buffer())
            data["datetime"] = pd.to_datetime(data['datetime'])

            return self.finally_parser(data, init_counter)
    
    async def get_timetravel(self, default: str = "timetravel") -> str:
        if not self.timetravel is None:
            return self.timetravel
        
        if "timetravel" not in self.xpath.keys():
            timetravel = default
        else:
            timetravel = await self.get_element(self.xpath["timetravel"]["xpath"], 
                                          text=True, name="timetravel")
        
            if not timetravel:
                self.driver.switch_to.default_content()
                timetravel = await self.get_element(self.xpath["timetravel"]["xpath"], 
                                              text=True, name="timetravel")
                self.switch_frame()

            if not timetravel:
                timetravel = default
            else:
                timetravel = RU_EN_timetravel[timetravel] if not timetravel.isdigit() else timetravel + "m"
        
        self.set_timetravel(timetravel)
        logger.debug(f"Get timetravel {timetravel=}")

        return timetravel
    
    def set_timetravel(self, timetravel: str):
        logger.debug(f"Set timetravel {self.timetravel=} -> {timetravel=}")
        self.timetravel = timetravel

    async def remove_timetravel(self, timetravel_page: str, timetravel: str = "5m"):
        logger.debug(f"Remove timetravel {timetravel_page=} != {timetravel=}")
        logger.debug(f"Replace timetravel to {timetravel}")
        
        for i in range(5):
            logger.debug(f"{i}/{5*min(self.tick, 1)} tick")
            timetravel = self.get_timetravel()

            if timetravel == timetravel_page:
                logger.debug(f"{timetravel} == {timetravel_page}")
                break

            asyncio.sleep(min(self.tick, 1))  

    def restart(self):
        super().restart()
        if self.login:
            self.entry(self.login, self.password)

    def login_xpath(self):
        self.add_xpath("login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div/div/input", parse=False)
        self.add_xpath("password", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[2]/div/div/input", parse=False)
        self.add_xpath("click_login", "/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/form/div[3]/button[1]", parse=False)

    def default_xpath(self):
        self.add_xpath("filename", "//h1[contains(@class,'lrtcss-c7k6qm')]", parse=False)
        self.add_xpath("timetravel", "//span[contains(@class,'value-data lrtcss-12xj9py')]", parse=False)
        self.add_xpath("frame", "iframe", parse=False)
        self.add_xpath("datetime", "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[4]/td[2]/div/canvas[2]", 
                       func_get=self.get_element_datetime, kwargs={"process": False,})
        self.add_xpath("open", "//div[2]/div[2]")
        self.add_xpath("max",  "/html/body/div[2]/div[1]/div[2]/div[1]/div[2]/table/tr[1]/td[2]/div/div[2]/div/div/div[2]/div/div[3]/div[2]")
        self.add_xpath("min", "//div[4]/div[2]")
        self.add_xpath("close", "//div[5]/div[2]")
        self.add_xpath("volume", "//div[contains(@class, 'valueValue-G1_Pfvwd apply-common-tooltip')]")