from ..api_error import API_ERROR


def get_new_token(refresh_token):
    grant_url = "https://www.worldcubeassociation.org/oauth/token"
    WCA_HEADERS = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "public manage_competitions",
    }
    response = requests.post(grant_url, data=WCA_HEADERS)
    if not response.ok:
        Logger.error("No connection to the WCA, or no access")
        raise API_ERROR(
            "get_new_token failed with error code {}".format(response.status_code)
        )
    response_json = response.json()
    wca_access_token = response_json["access_token"]
    wca_refresh_token = response_json["refresh_token"]
    with open(".secret", "w") as secret:
        print(
            str(datetime.datetime.now())
            + " token:"
            + wca_access_token
            + " refresh_token:"
            + wca_refresh_token,
            file=secret,
        )
