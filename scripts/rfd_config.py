import re

KEYWORDS = ("error", "lava", "dell", "lenovo", "s26")
IGNORES = ("lavazza",)
ROOT = "https://forums.redflagdeals.com"
SORT_URL = "/hot-deals-f9/?st=0&rfd_sk=tt&sd=d"
RE_ID = re.compile(r"-(\d+)/$")
