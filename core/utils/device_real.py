import pyautogui
from pynput import keyboard
from threading import Event, Lock
import time
import logging

logger = logging.getLogger("Device")

class Cursor:

    def __init__(self, tick=0.1):
        self.tick = tick
        self.position_cursor = {"start": None}
        self.scroll_direction = 0


    def set_position(self, types: list = ["start",]):
        for type in types:
            for try_pos in range(3):
                time.sleep(self.tick+3)
                logger.info(f"{try_pos=} {type=} Porsition cursor = {self.get_position_now()}")
            
            self.position_cursor[type] = self.get_position_now()
            logger.info(f"{type=} {self.position_cursor[type]=}")


    def add_position(self, type):
        self.position_cursor[type] = pyautogui.position()


    @property
    def get_position(self):
        return self.position_cursor
    
    @classmethod
    def get_position_now(cls):
        return pyautogui.position()


    def move_to_position(self, type:str = "start"):
        pyautogui.moveTo(*self.position_cursor[type], duration=self.tick)


    @classmethod
    def click(cls):
        pyautogui.click()


    def scroll(self, direction: int):
        pyautogui.scroll(direction)
        self.scroll_direction += direction 


    def scroll_to_start(self):
        self.scroll(-self.scroll_direction)


    def move(self, direction):

        if direction.endswith("fast"):
            interval = 2
        elif direction.endswith("middle"):
            interval = 1
        else:
            pyautogui.press(direction)
            return

        direction = direction.split("_")[0]
        pyautogui.hotkey("ctrl", direction, interval=interval)


class Keyboard:

    def __init__(self, tick=0.1):
        self.tick = tick
        self.stop_event = Event()  
        self.pause_event = Event()
        self.listener_lock = Lock()
        self.listener = None


    def on_press(self, key):
        try:
            char = key.char.lower()
        except AttributeError:
            return

        if char == 'q':
            self.stop_event.set()
            return False 
            
        elif char == 'p':
            with self.listener_lock:
                self.pause_event.clear() if self.pause_event.is_set() else self.pause_event.set()

        return True

    def listen_for_keypress(self):
        logger.info("Controls: [q] - Stop | [p] - Pause")
        with self.listener_lock:
            with keyboard.Listener(on_press=self.on_press) as self.listener:
                self.listener.join()

    def stop_listener(self):
        with self.listener_lock:
            if self.listener:
                self.listener.stop()
    
    def create_lfk(self, key: str, message: str = ">>>"):
        self.loop__ = False
        logger.info(message.format(key))
        keyboard.KeyCode.from_char(key)
        logger.info(f"Press '{key}'")
        self.loop__ = True
        return True

    def get_loop(self):
        return self.loop__
    
    def get_pause_loop(self):
        return self.pause_loop
    
    def get_stop_loop(self):
        return self.stop_loop
    
    def hotkey(self, *key: str, interval: int = 0):
        pyautogui.hotkey(*key, interval=self.tick+interval)


class Device:

    def __init__(self, tick=0.1):
        self.cursor = Cursor(tick)
        self.kb = Keyboard(tick)