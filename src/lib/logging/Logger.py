"""
    Central Logging platform (this is a wrapper class for logging, but we might
    need some extended feature)
"""
import logging


class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def error(self, msg):
        logging.warning(msg)

    def info(self, msg):
        logging.info(msg)
    
    def disable_logging(self):
        logging.basicConfig(level=logging.ERROR)
