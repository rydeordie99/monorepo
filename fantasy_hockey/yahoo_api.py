import logging
import os
from pathlib import Path

import httpx
from myutils.date_util import today

LEAGUE_ID = os.environ.get("YAHOO_LEAGUE_ID")
TEAM_ID = os.environ.get("YAHOO_TEAM_ID")
REFRESH_TOKEN_PATH = Path(__file__).parent / "yahoo.txt"


class Yahoo:
    def __init__(self) -> None:
        self.client_id = os.environ.get("YAHOO_CLIENT_ID")
        self.client_secret = os.environ.get("YAHOO_CLIENT_SECRET")
        self.headers = {}

        self.url = (
            f"https://fantasysports.yahooapis.com/fantasy/v2/team/"
            f"nhl.l.{LEAGUE_ID}.t.{TEAM_ID}/roster;date={today}"
        )

        self.get_access_token()

    def get_access_token(self) -> None:
        with REFRESH_TOKEN_PATH.open("r") as f:
            refresh_token = f.read()

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": "oob",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        logging.info("Getting new access token...")
        r = httpx.post(
            "https://api.login.yahoo.com/oauth2/get_token",
            data=data,
            auth=(os.environ.get("YAHOO_CLIENT_ID", ""), os.environ.get("YAHOO_CLIENT_SECRET", "")),
        ).json()

        with REFRESH_TOKEN_PATH.open("w") as f:
            f.write(r["refresh_token"])

        self.headers = {"Authorization": "Bearer " + r["access_token"]}

    def get_roster(self) -> str:
        logging.info("Getting roster...")
        return httpx.get(self.url, headers=self.headers).text

    def update_roster(self, data: str) -> None:
        logging.info("Updating roster...")
        headers = self.headers.copy()
        headers["Content-Type"] = "application/xml"
        httpx.put(self.url, headers=headers, data=data)  # type: ignore
