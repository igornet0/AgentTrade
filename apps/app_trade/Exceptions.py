
class OrderFulfilled(Exception):

    def __init__(self, message="Order fullfilled"):
        super().__init__(message)
