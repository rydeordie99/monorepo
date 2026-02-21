import re

import httpx
from bs4 import BeautifulSoup
from myutils.config import Setup
from myutils.email import send_email

s = Setup("bluray")

YEAR_CUTOFF = 2018

r = httpx.get("https://forum.blu-ray.com/forumdisplay.php?s=&f=203&sort=dateline&order=desc")

soup = BeautifulSoup(r.text, "html.parser")

pattern = re.compile(r"\d\d\d\d")

old = s.read_line()

for thread in soup.select("a[id*=thread_title]"):
    year = pattern.search(thread.text)
    if not year:
        continue

    year = int(year.group(0))

    if year > YEAR_CUTOFF:
        continue

    thread_id = str(thread.get("id")).split("_")[2]

    if thread_id in old:
        continue

    send_email("Blu-Ray.com", thread.text, f"https://forum.blu-ray.com/{thread.get('href')}")

    s.write_line(thread_id)

s.ping()
