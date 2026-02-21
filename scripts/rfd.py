from myutils.config import Setup
from myutils.email import send_email
from myutils.playwright import playwright_setup
from playwright.sync_api import Error

from .rfd_config import IGNORES, KEYWORDS, RE_ID, ROOT, SORT_URL

s = Setup("rfd")
old = s.read_line()


with playwright_setup() as page:
    page.goto(f"{ROOT}{SORT_URL}", wait_until="domcontentloaded")

    threads = []
    try:
        for row in page.locator("css=a.thread_title_link").all():
            thread_suffix = row.get_attribute("href")
            thread_id_match = RE_ID.search(thread_suffix)
            if (
                not thread_id_match
                or not any(keyword in thread_suffix for keyword in KEYWORDS)
                or any(ignore in thread_suffix for ignore in IGNORES)
                or thread_id_match.group(1) in old
            ):
                continue

            threads.append(thread_suffix)
            s.write_line(thread_id_match.group(1))
    except Error:
        ...

    for thread_suffix in threads:
        thread_url = ROOT + thread_suffix
        page.goto(thread_url, wait_until="domcontentloaded")

        content = (
            page.locator("css=div.post_content")
            .all()[0]
            .locator("css=div.content")
            .all()[0]
            .inner_text()
        )

        send_email("RFD", page.title(), f"{content}<br><br>{thread_url}")

s.ping()
