import pyautogui, keyboard
import time

class Cursor:

    def __init__(self, tick=0.1):
        self.tick = tick
        self.position_cursor = {"start": None}
        self.scroll_direction = 0


    def set_position(self, types: list = ["start",]):
        for type in types:
            for try_pos in range(3):
                time.sleep(self.tick+3)
                print(f"[INFO POSITION {try_pos}] {type=} Porsition cursor = {self.get_position_now()}")
            
            self.position_cursor[type] = self.get_position_now()
            print(f"[INFO SET POSITION] {type=} {self.position_cursor[type]=}")


    def add_position(self, type):
        self.position_cursor[type] = pyautogui.position()


    @property
    def get_position(self):
        return self.position_cursor
    

    def get_position_now(self):
        return pyautogui.position()


    def move_to_position(self, type:str = "start"):
        pyautogui.moveTo(*self.position_cursor[type], duration=self.tick)


    def click(self):
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
        self.stop_loop = False
        self.pause_loop = False

    def pause(self):
        while True:
            self.pause_loop = False
            print("[INFO] For pause press 'p'")
            keyboard.wait('p')
            self.pause_loop = True
            print("[INFO] Press 'p'")
            print("[INFO] For un pause press 'p'")
            keyboard.wait('p')
            print("[INFO] Press un 'p'")

    def listen_for_keypress(self):
        self.stop_loop = False
        print("[INFO] For stop press 'q'")
        keyboard.wait('q')
        print("[INFO] Press 'q'")
        self.stop_loop = True
        return True
    
    def get_pause_loop(self):
        return self.pause_loop
    
    def get_stop_loop(self):
        return self.stop_loop
    
    def hotkey(self, key, interval: int = 0):
        pyautogui.hotkey("ctrl", key, interval=self.tick+interval)

class Device:

    def __init__(self, tick=0.1):
        self.cursor = Cursor(tick)
        self.kb = Keyboard(tick)