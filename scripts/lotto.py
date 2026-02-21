import logging

import httpx
from bs4 import BeautifulSoup
from myutils.config import Setup
from myutils.telegram import send_telegram

MINIMUM_JACKPOT = 49

s = Setup("lotto")

r = httpx.get("https://www.wclc.com/careers.htm").text

soup = BeautifulSoup(r, "html.parser")

jackpots = soup.find_all("div", class_="nextJackpotDetails")

lotto_types = "Lotto 649", "Lotto Max"

for lotto_type, jackpot in zip(lotto_types, jackpots, strict=False):
    current = jackpot.find("div", class_="nextJackpotPrizeAmount").text
    logging.info("lotto_type: %s, current: %s", lotto_type, current)

    current_int = int(current)

    if current_int > MINIMUM_JACKPOT:
        secondary = jackpot.find("span", class_="nextJackpotSecondaryPrize")
        secondary = secondary.text if secondary else "N/A"

        body = (
            f"{lotto_type} is an estimated {current} million and {secondary}"
            f" 1 million dollar prizes"
        )

        send_telegram(body)

s.ping()
