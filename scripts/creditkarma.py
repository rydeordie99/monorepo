import logging
import os

from myutils.config import Setup
from myutils.playwright import playwright_setup
from myutils.telegram import send_telegram

s = Setup("creditkarma")

with playwright_setup(headless=False) as page:
    logging.info("getting login page")
    page.goto("https://www.creditkarma.ca/login")

    page.locator("[name='username']").fill(os.environ.get("CREDITKARMA_USER"))
    page.locator("[name='password']").fill(os.environ.get("CREDITKARMA_PASS"))
    page.get_by_role("button", name="Log in").click()
    logging.info("clicked login")

    score = page.get_by_test_id("score").inner_text()
    score_rating = page.get_by_test_id("credit_status").inner_text()

    logging.info("Score: %s", score)
    logging.info("Score rating: %s", score_rating)

    send_telegram(f"CreditKarma score is {score_rating} ({score}).")

s.ping()
