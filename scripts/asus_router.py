from itertools import zip_longest

import httpx
from myutils.config import Setup
from myutils.email import send_email

s = Setup("ac86u")

versions_old = s.read().split(",")

URL = "https://www.asus.com/support/api/product.asmx/GetPDBIOS"
MODELS = ("RT-AC86U", "RT-AX86U")
DB_CHANGE = False

versions_new = []
for model, version_old in zip_longest(MODELS, versions_old, fillvalue=""):
    params = {"website": "global", "model": model}

    r = httpx.get(URL, params=params).json()

    if r["Message"] == "SUCCESS":
        rj = r["Result"]["Obj"][0]["Files"][0]

        version = rj["Version"]
        versions_new.append(version)

        if version != version_old:
            send_email(
                model, rj["Title"], f"{rj['Description']}<br><br>{rj['DownloadUrl']['Global']}"
            )
            DB_CHANGE = True

if DB_CHANGE:
    s.write(",".join(versions_new))

s.ping()
