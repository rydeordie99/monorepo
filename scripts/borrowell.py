import logging
import os

from myutils.config import Setup
from myutils.playwright import playwright_setup
from myutils.telegram import send_telegram

s = Setup("borrowell")

with playwright_setup() as page:
    logging.info("getting login page")
    page.goto("https://app.borrowell.com/#/credit-factors")

    page.locator("[id='username']").fill(os.environ.get("BORROWELL_USER"))
    page.locator("[id='password']").fill(os.environ.get("BORROWELL_PASS"))
    page.get_by_role("button", name="Log in").click()
    logging.info("clicked login")

    score = page.locator("[data-cy='credit-score-text']").inner_text()
    score_rating = page.locator("[data-cy='score-status-text']").inner_text()
    score_change = page.locator("[data-cy='score-change-text']").inner_text()

    logging.info("Score: %s", score)
    logging.info("Score rating: %s", score_rating)
    logging.info("Score change: %s", score_change)

    send_telegram(f"Borrowell is {score} ({score_rating}. {score_change})")

s.ping()
