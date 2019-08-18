from lib.logging import Logger
from datetime import datetime
import requests, os, sys
from ..api_error import API_ERROR

l = Logger()

# Error handling for WCA website login errors
def error_handling_wcif(competition_name, competition_page):
    competition_name_stripped = competition_name.replace(" ", "")
    if "Not logged in" in competition_page:
        print("ERROR!!")
        print(
            "While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry."
        )
    elif "Competition with id" in competition_page:
        print("ERROR!!")
        print(
            "Competition with name {} not found on WCA website.".format(
                competition_name
            )
        )
    elif "Not authorized to manage" in competition_page:
        print("ERROR!!")
        print(
            "You are not authorized to manage this competition. Please only select your competitions."
        )
    elif "The page you were looking for doesn't exist." in competition_page:
        print("ERROR!!")
        print("Misstiped competition link, please enter correct link.")
    else:
        if not os.path.exists(competition_name_stripped):
            os.makedirs(competition_name_stripped)
        return None
    sys.exit()


# Get upcoming competitions of user
def get_upcoming_wca_competitions(password="", email="", access_token=""):
    start_date = str(datetime.today()).split()[0]
    url = "https://www.worldcubeassociation.org/api/v0/competitions?managed_by_me=true&start={}".format(
        start_date
    )

    if access_token == "":
        competition_wcif_info = wca_api(url, email, password)
    else:
        competition_wcif_info = wca_api(url, access_token)

    return competition_wcif_info.json()

def get_wcif_for_comp(
    competition_name, competition_name_stripped, email="", password="", access_token=""
):
    url = "https://www.worldcubeassociation.org/api/v0/competitions/{}/wcif".format(
        competition_name_stripped
    )

    if access_token == "":
        competition_wcif_info = wca_api(url, email, password)
    else:
        competition_wcif_info = wca_api(url, access_token)

    # Error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(competition_name, competition_wcif_info.text)

    return competition_wcif_info.text


# Simple request to get information about input competition name
def get_wca_competition(competition_name):
    url = "https://www.worldcubeassociation.org/api/v0/competitions/{}".format(
        competition_name.replace(" ", "")
    )

    competition_info = ""
    response = requests.get(url)
    if not response.ok:
        l.error("No connection to the WCA")
        raise API_ERROR(
            "wca_api failed with error code {}".format(response.status_code)
        )
    return response.json()


# Function to actually talk to WCA API and collect response information
def wca_api(request_url, email="", password="", access_token=""):
    grant_url = "https://www.worldcubeassociation.org/oauth/token"

    if access_token == "":
        wca_headers = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "scope": "public manage_competitions",
        }
        response = requests.post(grant_url, data=wca_headers)
        if not response.ok:
            l.error("No connection to the WCA")
            raise API_ERROR(
                "wca_api failed with error code {}".format(response.status_code)
            )
        data = response.json()
        wca_access_token = data["access_token"]
        wca_refresh_token = data["refresh_token"]
        with open(".secret", "w") as secret:
            print(
                str(datetime.now())
                + " token:"
                + wca_access_token
                + " refresh_token:"
                + wca_refresh_token,
                file=secret,
            )

    wca_authorization = "Bearer " + wca_access_token
    authorization_headers = {"Authorization": wca_authorization}
    competition_wcif_info = requests.get(request_url, headers=authorization_headers)

    return competition_wcif_info