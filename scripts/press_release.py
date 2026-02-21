import httpx
from myutils.config import Setup
from myutils.email import send_email

s = Setup("press_release")

old = s.read_line()

symbols = (
    ("N", "AMD"),
    ("N", "APPL"),
    ("T", "BCE"),
    ("T", "BIPC"),
    ("N", "BMRN"),
    ("T", "BNS"),
    ("T", "CHR"),
    ("T", "CIX"),
    ("T", "CM"),
    ("T", "CVE"),
    ("T", "CWB"),
    ("T", "ENB"),
    ("N", "IBM"),
    ("N", "KD"),
    ("T", "NA"),
    ("T", "NEXE"),
    ("N", "NVDA"),
    ("T", "POW"),
    ("T", "TD"),
    ("N", "TSLA"),
    ("N", "UWMC"),
)

for symbol in symbols:
    subject = body = ""
    if symbol[0] == "N":
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
        }
        r = httpx.get(
            f"https://www.nasdaq.com/api/news/topic/press_release?q=symbol:{symbol[1]}|assetclass:stocks&limit=10&offset=0",
            headers=headers,
        ).json()

        for news in r["data"]["rows"]:
            subject = news["title"]

            article_id = str(news["id"])
            title_lower = subject.lower()

            if article_id in old:
                continue

            if "financial results" not in title_lower:
                continue

            if any(x in title_lower for x in ("reports", "releases")):
                s.write_line(article_id)

                body = "https://www.nasdaq.com" + news["url"]
                send_email("StockNews", subject, body)

    if symbol[0] == "T":
        json_data = {
            "operationName": "getNewsAndEvents",
            "variables": {
                "symbol": symbol[1],
                "page": 1,
                "limit": 10,
                "locale": "en",
                "companyInNews": False,
            },
            "query": "query getNewsAndEvents($symbol: String!, $page: Int!, $limit: "
            "Int!, $locale: String!, $companyInNews: Boolean) {\n  news: "
            "getNewsForSymbol(\n    symbol: $symbol\n    page: $page\n    "
            "limit: $limit\n    locale: $locale\n    companyInNews: "
            "$companyInNews\n  ) {\n    headline\n    datetime\n    newsid\n    "
            "}\n  events: getUpComingEventsForSymbol(symbol: $symbol, locale: $locale) "
            "{\n    title\n    date\n    status\n    type\n    __typename\n  }"
            "\n}",
        }

        r = httpx.post("https://app-money.tmx.com/graphql", json=json_data).json()

        for news in r["data"]["news"]:
            subject = news["headline"]

            article_id = str(news["newsid"])
            title_lower = subject.lower()

            if article_id in old:
                continue

            if "results" not in title_lower:
                continue

            if any(x in title_lower for x in ("reports", "releases")):
                s.write_line(article_id)

                body = (
                    f"https://money.tmx.com/en/quote/{symbol[1]}/news/"
                    f"{news['newsid']}/{subject.replace(' ', '_')}"
                )
                send_email("StockNews", subject, body)

s.ping()
