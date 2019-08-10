"""
    Module for the functions that use the /persons endpoint of the wca "API"
"""
import requests
from lib.logging import Logger
from ..api_error import API_ERROR


def get_wca_competitor(wca_id):
    url = "https://www.worldcubeassociation.org/api/v0/persons/{}".format(wca_id)
    response = requests.get(url)
    if not response.ok:
        Logger.error("No connection to the WCA")
        raise API_ERROR("get_wca_competitor failed")
    competitor_info = response.json(wca_id)
    return competitor_info

