import apis
import os

def key_exists() -> bool:
    if not os.path.isfile(".secret"):
        return False
    with open(".secret", "r") as secret:
        secret_text = secret.read()
        secret_time = datetime.datetime.strptime(
            secret_text.split("token:")[0].strip(), "%Y-%m-%d %H:%M:%S.%f"
        )
        parser_args.access_token = (
            secret_text.split("token:")[1].split("refresh_")[0].strip()
        )
        refresh_token = secret_text.split("refresh_token:")[1].strip()
        return True

    if (secret_time - datetime.datetime.now()) > datetime.timedelta(hours=2):
        apis.wca_api_get_new_token(refresh_token)