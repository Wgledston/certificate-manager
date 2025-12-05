"""Main entry point for Certificate Manager."""

from selenium_core import BrowserManager, QuestorAuth, get_logger
from selenium_core.exceptions import SeleniumAutomationError
from .config import settings
from .company_processor import CompanyProcessor


logger = get_logger(__name__, log_dir=settings.LOGS_DIR)


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Certificate Manager - Starting")
    logger.info("=" * 60)
    
    driver = None
    
    try:
        # Create browser
        logger.info("Initializing browser...")
        driver = BrowserManager.create_driver(
            headless=settings.HEADLESS,
            window_size=settings.WINDOW_SIZE,
            chrome_binary=settings.CHROME_BINARY,
            block_images=settings.BLOCK_IMAGES
        )
        
        # Login
        logger.info("Authenticating...")
        QuestorAuth.login(
            driver,
            settings.APP_URL,
            settings.APP_USERNAME,
            settings.APP_PASSWORD
        )
        
        # Process companies
        logger.info("Processing companies...")
        processor = CompanyProcessor(driver)
        processor.process_from_csv(str(settings.DATA_DIR / settings.DATA_FILE))
        
        logger.info("=" * 60)
        logger.info("Certificate Manager - Completed Successfully")
        logger.info("=" * 60)
        
    except SeleniumAutomationError as e:
        logger.error(f"Automation error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
