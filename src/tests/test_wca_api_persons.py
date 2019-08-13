import requests
import responses
import unittest

class TestAPIPersons(unittest.TestCase):
    # This can actually be done without Mocking as the there are 
    # no authorized requests in this part of the API 
    def setUp(self):
        pass
    
    def test_get_wca_competitor(self):
        test_competitors = []