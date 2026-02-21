import contextlib
import logging
from collections.abc import Generator

from playwright.sync_api import sync_playwright


@contextlib.contextmanager
def playwright_setup(headless: bool = True) -> Generator:
    with sync_playwright() as playwright:
        try:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                headless = False

            browser = playwright.chromium.launch(
                args=["--deny-permission-prompts"], headless=headless
            )

            context = browser.new_context(
                viewport={"width": 960, "height": 1050},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/136.0.7103.25 Safari/537.36",
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            page = context.new_page()
            yield page
        finally:
            logging.info("quitting browser")
