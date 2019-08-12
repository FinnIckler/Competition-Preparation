from lib.api.wca import get_new_token
import os
import datetime


def key_exists() -> bool:
    return os.path.isfile(".secret")


def get_key() -> str:
    with open(".secret", "r") as secret:
        secret_text = secret.read()
        secret_time = datetime.datetime.strptime(
            secret_text.split("token:")[0].strip(), "%Y-%m-%d %H:%M:%S.%f"
        )
        access_token = secret_text.split("token:")[1].split("refresh_")[0].strip()
        refresh_token = secret_text.split("refresh_token:")[1].strip()

    # Refresh if necessary
    if (secret_time - datetime.datetime.now()) > datetime.timedelta(hours=2):
        get_new_token(refresh_token)

    return access_token
