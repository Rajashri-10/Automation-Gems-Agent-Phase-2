from src.config import load_config
from src.csv_reader import CSVReader
from src.validators import validate_records
from src.logger import setup_logger
from src.browser import BrowserManager
from src.agent_creator import AgentCreator
from src.agent_verifier import AgentVerifier


def main():

    logger = setup_logger()

    logger.info(
        "Starting CSV → Gemini Enterprise automation"
    )

    config = load_config()

    logger.info(
        f"CSV: {config.csv_path}"
    )

    # ------------------------------------------
    # 1. Read CSV
    # ------------------------------------------

    reader = CSVReader(
        config.csv_path
    )

    records = reader.get_records()

    logger.info(
        f"Total CSV records: {len(records)}"
    )

    # ------------------------------------------
    # 2. Validate CSV
    # ------------------------------------------

    valid_records, invalid_records = (
        validate_records(records)
    )

    logger.info(
        f"Valid records: {len(valid_records)}"
    )

    logger.info(
        f"Invalid records: {len(invalid_records)}"
    )

    for invalid in invalid_records:

        logger.error(
            f"Row {invalid['row_number']}: "
            f"{invalid['error']}"
        )

    # ------------------------------------------
    # 3. Apply test limit
    # ------------------------------------------

    records_to_process = valid_records

    if config.test_limit > 0:

        records_to_process = (
            valid_records[
                :config.test_limit
            ]
        )

    logger.info(
        f"Records selected for processing: "
        f"{len(records_to_process)}"
    )

    # ------------------------------------------
    # 4. Connect browser
    # ------------------------------------------

    browser = BrowserManager(
        cdp_url=config.cdp_url,
        navigation_timeout=(
            config.navigation_timeout
        ),
        action_timeout=(
            config.action_timeout
        ),
    )

    try:

        page = browser.connect()

        logger.info(
            "Connected to existing Chrome session."
        )

        # --------------------------------------
        # 5. Open Gemini Enterprise
        # --------------------------------------

        if not config.gemini_enterprise_url:
            raise ValueError(
                "GEMINI_ENTERPRISE_URL "
                "is not configured."
            )

        page.goto(
            config.gemini_enterprise_url
        )

        logger.info(
            "Gemini Enterprise opened."
        )

        # --------------------------------------
        # 6. Agent Creator
        # --------------------------------------

        creator = AgentCreator(
            page=page,
            dry_run=config.dry_run,
        )

        verifier = AgentVerifier(
            page=page
        )

        # --------------------------------------
        # 7. Process agents
        # --------------------------------------
        
        import csv
        import os
        from datetime import datetime
        
        results = []

        for record in records_to_process:
            logger.info(f"Processing agent: {record['name']}")
            success = False
            error_msg = ""
            screenshot_path = ""
            try:
                # Ensure a clean slate on the agents dashboard
                page.goto(config.gemini_enterprise_url, wait_until="domcontentloaded")
                page.wait_for_timeout(1500)
                creator.dismiss_any_dialogs()
                creator.open_agent_builder()
                creator.fill_agent(record)
                creator.validate_form()

                # Save evidence before create
                browser.screenshot(f"1_before_create_{record['row_number']}.png")

                created = creator.create_agent()

                if config.dry_run:
                    logger.info(f"DRY RUN completed for {record['name']}")
                    success = True
                    results.append({
                        "row_number": record["row_number"],
                        "name": record["name"],
                        "status": "SUCCESS",
                        "error": "",
                        "timestamp": datetime.now().isoformat(),
                        "screenshot": f"1_before_create_{record['row_number']}.png"
                    })
                    # Reset back to home page for next agent
                    page.goto(config.gemini_enterprise_url)
                    continue

                # Wait for creation success
                creator.wait_for_creation_success()
                browser.screenshot(f"2_after_create_{record['row_number']}.png")

                # Post-creation flow
                creator.click_chat_with_agent()
                browser.screenshot(f"3_chat_with_agent_{record['row_number']}.png")

                creator.return_to_agents_page()
                creator.verify_agents_page()
                browser.screenshot(f"4_returned_to_agents_{record['row_number']}.png")

                logger.info(f"SUCCESS: {record['name']}")
                success = True

            except Exception as error:
                logger.exception(f"Failed to process {record['name']}: {error}")
                error_msg = str(error)
                screenshot_path = f"error_{record['row_number']}_{record['name'].replace(' ', '_')}.png"
                browser.screenshot(screenshot_path)
                
                # Try to navigate back to a clean state for the next record
                try:
                    page.goto(config.gemini_enterprise_url)
                except:
                    pass

            results.append({
                "row_number": record["row_number"],
                "name": record["name"],
                "status": "SUCCESS" if success else "FAILED",
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "screenshot": screenshot_path if not success else f"4_returned_to_agents_{record['row_number']}.png"
            })
            
        # Write results
        os.makedirs("output", exist_ok=True)
        with open("output/migration_results.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["row_number", "name", "status", "error", "timestamp", "screenshot"])
            writer.writeheader()
            writer.writerows(results)
            
        logger.info("Saved output/migration_results.csv")

    finally:

        browser.close()

        logger.info(
            "Automation finished."
        )


if __name__ == "__main__":
    main()