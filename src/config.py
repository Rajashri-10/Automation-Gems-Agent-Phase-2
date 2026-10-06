import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load values from .env
load_dotenv()


@dataclass
class Config:
    # CSV
    csv_path: str

    # Gemini Enterprise
    gemini_enterprise_url: str

    # Browser
    cdp_url: str
    headless: bool

    # Automation
    dry_run: bool
    test_limit: int
    max_retries: int

    # Timeouts
    navigation_timeout: int
    action_timeout: int

    # Debug
    debug: bool


def _get_bool(
    name: str,
    default: bool = False,
) -> bool:

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "y",
    }


def _get_int(
    name: str,
    default: int,
) -> int:

    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    return int(value)


def load_config() -> Config:

    return Config(

        # ----------------------------------
        # CSV
        # ----------------------------------

        csv_path=os.getenv(
            "CSV_PATH",
            "data/agents.csv",
        ),

        # ----------------------------------
        # Gemini Enterprise
        # ----------------------------------

        gemini_enterprise_url=os.getenv(
            "GEMINI_ENTERPRISE_URL",
            "",
        ),

        # ----------------------------------
        # Browser
        # ----------------------------------

        cdp_url=os.getenv(
            "CDP_URL",
            "http://127.0.0.1:9222",
        ),

        headless=_get_bool(
            "HEADLESS",
            False,
        ),

        # ----------------------------------
        # Automation
        # ----------------------------------

        dry_run=_get_bool(
            "DRY_RUN",
            True,
        ),

        test_limit=_get_int(
            "TEST_LIMIT",
            1,
        ),

        max_retries=_get_int(
            "MAX_RETRIES",
            2,
        ),

        # ----------------------------------
        # Timeouts
        # ----------------------------------

        navigation_timeout=_get_int(
            "NAVIGATION_TIMEOUT",
            30000,
        ),

        action_timeout=_get_int(
            "ACTION_TIMEOUT",
            15000,
        ),

        # ----------------------------------
        # Debug
        # ----------------------------------

        debug=_get_bool(
            "DEBUG",
            True,
        ),
    )