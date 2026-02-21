import contextlib
from pathlib import Path

import httpx

urls = (
    "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt",
    "https://v.firebog.net/hosts/AdguardDNS.txt",
    "https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt",
    "https://v.firebog.net/hosts/Easylist.txt",
    "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=&showintro=0&mimetype=plaintext",
    "https://v.firebog.net/hosts/Easyprivacy.txt",
    "https://v.firebog.net/hosts/Prigent-Ads.txt",
    "https://gitlab.com/quidsup/notrack-blocklists/raw/master/notrack-blocklist.txt",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/data/add.2o7Net/hosts",
    "https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt",
)

combined = set()
for url in urls:
    r = httpx.get(url).text
    for line in r.splitlines():
        if line.startswith("#") or line == "":
            continue
        if line.startswith("0.0.0.0"):
            line = line.removeprefix("0.0.0.0")
        if line.startswith("127.0.0.1"):
            line = line.removeprefix("127.0.0.1")
        line = line.split()[0].strip()
        combined.add(line)

WHITELIST_FILE = Path("whitelist.txt")
OUTPUT_FILE = Path("unbound-ads.conf")

whitelist = WHITELIST_FILE.read_text(encoding="utf-8")

for whitelist_item in whitelist:
    with contextlib.suppress(KeyError):
        combined.remove(whitelist_item)

sorted_list = sorted(combined)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    for line in sorted_list:
        f.write(f'local-zone: "{line}" refuse\n')
