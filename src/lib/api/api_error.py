class API_ERROR(Exception):
    def __init__(self, message):
        self.message = message