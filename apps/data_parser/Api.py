from abc import abstractmethod
import asyncio

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException

import pandas as pd
from PIL import Image

from typing import Any, Callable, Union, Generator
import base64, json
import threading
from io import BytesIO
from datetime import datetime
from shutil import rmtree
from os import path, listdir, mkdir

from core.utils.device_real import Device
from core.utils.tesseract_img_text import image_to_text, str_to_datatime
from core.utils.web_driver import WebDriver, WebOptions
from core.config import settings_trade

from apps.data_parser import DataParser

import logging

logger = logging.getLogger("parser_logger.Api")

class ParserApi:

    def __init__(self, tick: int = 1, driver = None, save: bool = False, import_device: bool = True) -> None:

        self.driver = WebDriver if driver is None else driver
        self.URL = None
        self.flag_open_web = False

        self.save = save
        self.filename = "data.csv"
        self.path_trach = settings_trade.TRACH_PATH
        self.path_save = settings_trade.RAW_DATA_PATH 
        self.name_launch = "launch_parser"

        self.tick = tick

        self.xpath = {}

        self.device = Device
        self.buffer_date = []
        self.buffer_data = []

        self.default_options = WebOptions() 

        if import_device:
            self.import_device()

    def import_device(self, device: Device = None) -> None:
        self.device = device if device is not None else self.device(self.tick)

        self.keypress_thread = threading.Thread(target=self.device.kb.listen_for_keypress, daemon=True)
        self.keypress_thread.start()

    def open_driver(self, options=None, use_subprocess: bool=True) -> WebDriver:
        if self.driver is None:
            raise ValueError("Driver not found")
        
        self.driver = self.driver(options=options, use_subprocess=use_subprocess)

        return self.driver

    def set_options(self, new_options: WebOptions) -> None:
        self.default_options = new_options

    def add_data_buffer(self, data: dict):
        self.buffer_data.append(data)

    def get_data_buffer(self) -> list[datetime]:
        return self.buffer_data
    
    def clear_data_buffer(self):
        self.buffer_data = []

    async def entry(self, login: str, password: str):
        if not self.driver:
            raise ValueError("Driver not found")
        
        assert self.flag_open_web, "Web not open"
        
        assert login and password, "Login or password is empty"

        assert self.xpath.get("login") is not None
        assert self.xpath.get("password") is not None
        assert self.xpath.get("click_login") is not None

        self.wait_for_page_load()

        self.login = login
        self.password = password

        await self.get_element(self.xpath["login"]["xpath"], name="login")[0].send_keys(login)
        await self.get_element(self.xpath["password"]["xpath"], name="password")[0].send_keys(password)
        await self.get_element(self.xpath["click_login"]["xpath"], name="click_login")[0].click()

        logger.info(f"Entry {login=}")

        return True

    async def start_web(self, URL:str = None, show_browser: bool = True, window_size: tuple = (1100, 1000)) -> WebDriver:
        if self.driver is None or not self.flag_open_web:

            if not show_browser:
                self.default_options.add_argument("--headless=new")

            self.open_driver(self.default_options)

        elif self.flag_open_web:
            return self.driver
        
        if show_browser:
            self.driver.set_window_size(*window_size)

        self.driver.get(URL) 
        asyncio.sleep(3)

        self.driver.switch_to.default_content()

        self.URL = URL

        logger.info(f"Start web {URL=}")
        self.flag_open_web = True

        return self.driver
    
    @abstractmethod
    async def start_parser(self, counter: int = 1) -> pd.DataFrame:
        pass

    def close(self) -> bool:
        if self.driver is None or not self.flag_open_web:
            return False
        
        self.driver.quit()
        self.flag_open_web = False
        return True
    
    async def restart(self):
        assert self.URL is not None

        self.close()
        await self.start_web(self.URL)
    
    async def switch_frame(self, frame: str = "frame") -> bool:
        assert self.xpath.get(frame) is not None
        assert self.driver is not None
        try:
            frame = await self.get_element(self.xpath[frame]["xpath"], by=By.TAG_NAME, name="frame")
            self.driver.switch_to.frame(frame) 
        except Exception as e:
            logger.error(f"Switch frame error: {e}")
            return False
        
        return True

    def click(self, element: WebElement) -> None:
        assert self.driver is not None
        
        try:
            element.click()
        except Exception as e:
            logger.error(f"Click error: {e}")

    def search_element_text(self, elements, text):

        for element in elements:
            if text and text in element.text.strip().replace("\n", "").lower():
                return element
            
        return False
    
    def add_xpath(self, key:str, xpath:str, parse:bool = True, 
                  func_get:Callable | None = None, args: tuple = (), kwargs: dict = {}) -> None:
        
        self.xpath[key] = {"xpath": xpath, "parse": parse, 
                           "func_get": func_get, "args": args, "kwargs": kwargs}

    async def get_elements(self) -> DataParser:
        data_d = DataParser()
        for key, xpath_data in self.xpath.items():
            xpath, parse, func_get = xpath_data["xpath"], xpath_data["parse"], xpath_data["func_get"]
            if not parse:
                continue

            logger.debug(f"Get element {key=}")

            if not func_get is None:
                args, kwargs = xpath_data["args"], xpath_data["kwargs"]

                element = await func_get(*args, **kwargs)
            else:
                element = await self.get_element(xpath, text=True, name=key)

            if not element:
                logger.error(f"Element {key} not found")
                
            data_d[key] = element

        return data_d

    async def get_element(self, xpath:str, by=By.XPATH, name="element", text=False, all=False) -> Union[str, list]:
        assert self.driver is not None

        iter = 20
        while True:
            try:
                if all:
                    element = WebDriverWait(self.driver, max(self.tick, 1)).until(
                            EC.presence_of_all_elements_located((by, xpath))
                        )
                else:
                
                    element = WebDriverWait(self.driver, max(self.tick, 1)).until(
                            EC.presence_of_element_located((by, xpath))
                        )

                if element is None:
                    raise ValueError(f"element {xpath} is None")

                if text:
                    if all:
                        return [e.text if e.text else "" for e in element]
                    
                    if not element.text:
                        raise ValueError(f"element {xpath} not text")

                    return element.text
                
                return element

            except Exception as e:
                iter -= 1
                asyncio.sleep(self.tick)
                if iter == 0:
                    n_error = len(list(filter(lambda x: x.endswith('_screenshot_error.png'), listdir(self.path_trach)))) + 1
                    self.driver.save_screenshot(path.join(self.path_trach, "img", f"{n_error}_screenshot_error.png"))

                    logger.error(f"error:{n_error} Not found element {name=}")
                    break

    def set_filename(self, filename: str):
        self.filename = filename

    def wait_for_page_load(self, timeout=30):
        """
        Ожидает полной загрузки страницы
        :param timeout: максимальное время ожидания в секундах
        :return: True если страница загружена, False при таймауте
        """
        assert self.driver is not None

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
                and len(d.find_elements(By.TAG_NAME, "body")) > 0
            )
            logger.info("Страница загружена")
            return True
        except TimeoutException:
            logger.error("Таймаут ожидания загрузки страницы")
            return False
    
    def finally_parser(self, data: pd.DataFrame, counter: int = 1):
        if len(data) != counter:
            logger.info(f"{len(data)}/{counter}")
            
        if len(data) == 0:
            logger.info("No data")
            return (None, None)
        
        datetime_last = data['datetime'].min()
        logger.info(f"Last datetime = {datetime_last}")
        logger.info("End parser")

        return (datetime_last, self.save_data(data)) if self.save else (datetime_last, data)
    
    def wrapper_gen(self, func: Callable, *args: tuple, **kwargs: dict) -> Generator[Any, None, None]:
        yield func(*args, **kwargs)

    async def get_element_datetime(self, process=False) -> datetime | Generator[datetime, None, None]:
        error_buffer = []
        while True:
            try:
                element = await self.get_element(self.xpath["datetime"]["xpath"], name="datetime")
                img = self.get_img(element)

                if img:
                    if process:
                        date = self.get_datetime(img)
                        if not date:
                            raise ValueError("Date not found")
                    else:
                        date = self.wrapper_gen(self.get_datetime, img)
                    
                    return date
                
                raise ValueError("Image not found")
            
            except ValueError:
                error_buffer.append(date)
                if len(error_buffer) > 10:
                    logger.error(f"error_buffer = {set(error_buffer)}")
                    return None
                
    def get_img(self, element: WebElement) -> Image:
        image_data = base64.b64decode(self.driver.execute_script('return arguments[0].toDataURL().substring(21);', element))
        img = Image.open(BytesIO(image_data))

        return img

    def get_datetime(self, img: Image) -> datetime | None:
        try:
            text = image_to_text(img)
            date = str_to_datatime(text)
        except Exception as e:
            img.save(path.join(self.path_trach, "img", f"{len(list(filter(lambda x: x.endswith('_error.png'), listdir(self.path_trach)))) + 1}_error.png"))
            self.driver.save_screenshot(path.join(self.path_trach, "img", f"{len(list(filter(lambda x: x.endswith('screenshot_error.png'), listdir(self.path_trach)))) + 1}_screenshot_error.png"))
            logger.error(f"Get datetime error: {e}")
            date = None
        
        return date
        
    async def handler_loop(self) -> bool:
        if self.device.kb.stop_event.is_set():
            logger.info("Stop parser by keypress")
            return False
            
        if self.device.kb.pause_event.is_set():
            logger.info("Pause parser by keypress")
            while self.device.kb.pause_event.is_set():
                asyncio.sleep(0.5)  
                if self.device.kb.stop_event.is_set():
                    return False
            logger.info("Resuming parser")
        return True

    async def search_datetime(self, target_datetime: datetime, right_break: bool = False, ) -> bool:
        buffer_life = 3
        logger.info(f"Search datetime {target_datetime}")

        self.device.cursor.scroll_to_start()
        while True:

            if not await self.handler_loop():
                return False
            
            date = await self.get_element_datetime(process=True) or self.get_last_buffer_date()

            if date is None:
                continue

            self.buffer_date.append(date)

            delta = abs((target_datetime - date).total_seconds())

            if delta == 0:
                logger.info(f"datetime {target_datetime} found")
                self.buffer_date = []
                return True
            
            if self.should_clear_buffer():
                date = self.buffer_date[-1]
                buffer_life -= 1
                logger.debug(f"clear buffer")

                if buffer_life == 0:
                    self.device.cursor.scroll(-25)
                    logger.info(f"datetime {target_datetime} not found")
                    logger.info(f"buffer {self.buffer_date}")
                    return False
                
                self.buffer_date = []
                self.device.cursor.scroll(25)
            
            direction = self.determine_direction(target_datetime, date)
            if direction == "right" and right_break:
                break
            
            interval = self.determine_interval(delta)
            self.device.cursor.move(direction + interval)
            self.device.cursor.move_to_position()

        return True

    def get_last_buffer_date(self) -> datetime | None:
        return self.buffer_date[-1] if self.buffer_date else None

    def should_clear_buffer(self) -> bool:
        if len(self.buffer_date) > 10:
            if len(set(self.buffer_date)) <= 5:
                return True
        return False

    def determine_direction(self, target_datetime: datetime, date: datetime) -> str:
        if target_datetime < date:
            return "left"
        else:
            return "right"

    def determine_interval(self, delta: float) -> str:
        if delta / 60 < 60 * 4:
            return ""
        if delta / 60 < 60 * 8:
            return "_middle"
        else:
            return "_fast"
        
    def set_save_trach(self, path:str):
        self.path_trach = path

    def save_data(self, data) -> pd.DataFrame:
        path_save = self.create_launch_dir()
        data.to_csv(path.join(path_save, self.filename), index=False)
        return data
    
    def create_launch_dir(self) -> str:
        n = len([f for f in listdir(self.path_save) if f.startswith(self.name_launch)]) + 1

        mkdir(path.join(self.path_save, f"{self.name_launch}_{n}"))
        return path.join(self.path_save, f"{self.name_launch}_{n}")

    def remove_launch_dir(self, launch_number: int) -> None:
        path_remove = path.join(self.path_save, f"{self.name_launch}_{launch_number}")
        rmtree(path_remove)

    async def rec_xpath(self, url):
        "TEST"
        await self.start_web(url)    

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
            asyncio.sleep(0.5)

            [xpath.setdefault(c, set()).add(x) for x, c in zip(self.driver.execute_script("return getXpathList()"), self.driver.execute_script("return getclassNamesList()"))]

            if not await self.handler_loop():
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
        
        self.close()
