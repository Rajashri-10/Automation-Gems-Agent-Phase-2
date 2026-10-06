class AgentVerifier:

    def __init__(self, page):
        self.page = page

    def verify(
        self,
        agent_name: str,
    ) -> bool:

        # Wait for Creating... button to disappear
        try:
            self.page.get_by_text("Creating...", exact=True).wait_for(state="hidden", timeout=30000)
        except Exception:
            pass

        locator = self.page.get_by_text(
            agent_name,
            exact=False,
        ).first

        try:
            locator.wait_for(
                state="visible",
                timeout=10000,
            )

            return True

        except Exception:
            return False