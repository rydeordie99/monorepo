import logging
from pathlib import Path

import httpx

REFRESH_TOKEN_PATH = Path(__file__).parent.parent / "host" / "questrade.txt"
AUTH_URL = "https://login.questrade.com/oauth2/token"


class Questrade:
    def __init__(self) -> None:
        self.headers = self.api_server = None
        self.get_auth()

    def get_auth(self) -> None:
        with REFRESH_TOKEN_PATH.open() as f:
            refresh_token = f.read()

        r = httpx.get(f"{AUTH_URL}?grant_type=refresh_token&refresh_token={refresh_token}").json()

        logging.info("response: %s", r)

        with REFRESH_TOKEN_PATH.open("w") as f:
            f.write(r["refresh_token"])

        self.headers = {"Authorization": "Bearer " + r["access_token"]}

        self.api_server = r["api_server"]

    def get_activity(self, account: str, start_time: str, end_time: str) -> dict:
        api_url = (
            f"{self.api_server}v1/accounts/{account}/activities?"
            f"startTime={start_time}&endTime={end_time}"
        )
        return httpx.get(api_url, headers=self.headers).json()
