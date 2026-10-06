from pathlib import Path
# pyright: ignore [reportMissingImports]
from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(
        self,
        cdp_url: str,
        navigation_timeout: int,
        action_timeout: int,
    ):
        self.cdp_url = cdp_url

        self.navigation_timeout = (
            navigation_timeout
        )

        self.action_timeout = action_timeout

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def connect(self):

        self.playwright = (
            sync_playwright().start()
        )

        self.browser = (
            self.playwright.chromium
            .connect_over_cdp(
                self.cdp_url
            )
        )

        contexts = self.browser.contexts

        if not contexts:
            raise RuntimeError(
                "No browser context found."
            )

        self.context = contexts[0]

        pages = self.context.pages

        if pages:
            self.page = pages[0]
        else:
            self.page = (
                self.context.new_page()
            )

        self.page.set_default_timeout(
            self.action_timeout
        )

        self.page.set_default_navigation_timeout(
            self.navigation_timeout
        )
        
        self.page.set_viewport_size({"width": 1920, "height": 1080})

        return self.page

    def get_page(self):
        if self.page is None:
            raise RuntimeError(
                "Browser is not connected."
            )

        return self.page

    def screenshot(
        self,
        filename: str,
    ):

        directory = Path(
            "artifacts/screenshots"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / filename

        self.page.screenshot(
            path=str(path),
            full_page=True,
        )

        return path

    def close(self):
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass