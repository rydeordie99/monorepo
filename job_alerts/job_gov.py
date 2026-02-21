import logging
from io import StringIO

from myutils.config import Setup
from myutils.email import send_email
from myutils.playwright import playwright_setup

s = Setup("job_gov")

old = s.read_line()

ROOT = "https://jobpostings.alberta.ca"
KEYWORDS = ("community", "social", "health", "child")

with playwright_setup() as page:
    logging.info("Navigating to page")
    page.goto(f"{ROOT}/search/")

    logging.info("clicking options")
    page.get_by_role("button", name="Show More Options").click()

    logging.info("Choosing city")
    page.get_by_placeholder("Location").fill("Edmonton")

    ministry_dropdown = page.locator("[id='optionsFacetsDD_customfield1']")
    all_jobs = []
    for option in ministry_dropdown.get_by_role("option").all():
        if any(keyword in option.inner_text().lower() for keyword in KEYWORDS):
            logging.info("Selecting category: %s", option.inner_text())
            ministry_dropdown.select_option(option.inner_text())
            page.get_by_role("button", name="Search Jobs").click()

            all_jobs.extend(
                {
                    "name": job.get_by_role("link").inner_text(),
                    "url": ROOT + job.get_by_role("link").get_attribute("href"),
                }
                for job in page.get_by_role("row").all()[2:]
            )

    for job in all_jobs:
        if job["url"] in old:
            continue

        page.goto(job["url"])

        subject = f"GoA Jobs: {job['name']}"
        html = StringIO()
        html.write(job["url"])
        html.write("<br><br>")
        html.write(page.locator("css=div.job").inner_html())

        logging.info(job["name"])
        send_email("JobPostings", subject, html.getvalue())

        s.write_line(job["url"])

s.ping()
