"""
    Module for the functions that use the /persons endpoint of the wca "API"
"""
import requests
import math
from lib.logging import Logger
from ..api_error import API_ERROR
from typing import List

l = Logger()

def get_wca_competitor(wca_id: str) -> dict:
    url = "https://www.worldcubeassociation.org/api/v0/persons/{}".format(wca_id)
    response = requests.get(url)
    if not response.ok:
        print(url)
        l.error("No connection to the WCA")
        raise API_ERROR(
            "get_wca_competitor failed with error code {}".format(response.status_code)
        )
    competitor_info = response.json()
    return competitor_info


def get_wca_competitors(wca_ids: List[str]) -> List[dict]:
    competitors_info = []
    BATCH_SIZE = 100
    # Split WCA IDs up into batches of 100 each time and request information from WCA API
    for competitors in range(0, math.ceil(len(wca_ids) / BATCH_SIZE)):
        wca_ids_partial = wca_ids[
            competitors * BATCH_SIZE : (competitors + 1) * BATCH_SIZE
        ]
        url = "https://www.worldcubeassociation.org/api/v0/persons?wca_ids={}&per_page={}".format(
            ",".join(wca_ids_partial), BATCH_SIZE
        )

        response = requests.get(url)

        if not response.ok:
            l.error("No connection to the WCA or Malformed URL")
            raise API_ERROR(
                "get_wca_competitors failed with error code {}".format(
                    response.status_code
                )
            )

        competitors_info.extend(response.json())

    return competitors_info
