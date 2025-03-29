import threading

class Thread(threading.Thread):

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self._args = args
        self._kwargs = kwargs
    
        self.result = None

    def run(self):
        self.result = self.func(*self._args, **self._kwargs)

    def get_result(self):
        return self.result