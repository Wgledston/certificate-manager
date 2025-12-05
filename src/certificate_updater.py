"""Certificate updater module."""

import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium_core.waits import wait_and_click, wait_for_element
from selenium_core.logger import get_logger
from selenium_core.exceptions import CertificateError

logger = get_logger(__name__)


class CertificateUpdater:
    """Handles certificate update operations."""
    
    def __init__(self, driver: Chrome):
        """
        Initialize certificate updater.
        
        Args:
            driver: Chrome WebDriver instance
        """
        self.driver = driver
    
    def update_certificate(
        self,
        inscricao: str,
        certificate_path: str,
        password: str
    ) -> None:
        """
        Update certificate for a company.
        
        Args:
            inscricao: Company federal inscription
            certificate_path: Path to certificate file
            password: Certificate password
            
        Raises:
            CertificateError: If update fails
        """
        try:
            logger.info(f"Updating certificate for inscription: {inscricao}")
            
            # Select all checkbox
            self._toggle_select_all()
            
            # Open actions menu
            wait_and_click(self.driver, By.XPATH, '//*[@id="actions"]/button')
            
            # Click edit certificates
            wait_and_click(self.driver, By.ID, 'edit-certs')
            
            time.sleep(0.5)
            
            # Upload certificate
            self._upload_certificate(certificate_path)
            
            # Fill password
            self._fill_password(password)
            
            # Confirm
            wait_and_click(self.driver, By.ID, 'confirm-edit-certs')
            
            # Try to close modal
            self._close_modal()
            
            logger.info(f"Certificate updated successfully for {inscricao}")
            
        except Exception as e:
            logger.error(f"Failed to update certificate for {inscricao}: {e}")
            raise CertificateError(f"Certificate update failed: {e}") from e
    
    def _toggle_select_all(self) -> None:
        """Toggle select all checkbox."""
        checkbox = wait_for_element(
            self.driver,
            By.XPATH,
            '//*[@id="def-table"]/thead/tr[2]/th[1]/label/input',
            timeout=30,
            condition='clickable'
        )
        
        if checkbox.is_selected():
            checkbox.click()  # Uncheck
            time.sleep(0.5)
        
        checkbox.click()  # Check
    
    def _upload_certificate(self, certificate_path: str) -> None:
        """Upload certificate file."""
        upload_input = wait_for_element(
            self.driver,
            By.XPATH,
            '//*[@id="fine-uploader"]/div/div[2]/input',
            timeout=30
        )
        
        try:
            upload_input.send_keys(certificate_path)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to upload certificate: {e}")
            # Try to close modal on error
            try:
                wait_and_click(
                    self.driver,
                    By.XPATH,
                    '//*[@id="boxEditCertClient"]/div/div/div[1]/button',
                    timeout=5
                )
            except:
                pass
            raise
    
    def _fill_password(self, password: str) -> None:
        """Fill certificate password."""
        password_field = wait_for_element(
            self.driver,
            By.ID,
            'Certificate_Password',
            timeout=30,
            condition='visible'
        )
        
        wait_for_element(
            self.driver,
            By.ID,
            'Certificate_Password',
            timeout=10,
            condition='clickable'
        )
        
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
    
    def _close_modal(self) -> None:
        """Try to close modal after update."""
        try:
            wait_and_click(
                self.driver,
                By.XPATH,
                '//*[@id="boxEditCertClient"]/div/div/div[1]/button',
                timeout=5
            )
        except Exception:
            logger.debug("Modal close button not found or not clickable")
