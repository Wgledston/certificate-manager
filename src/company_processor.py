"""Company processor module."""

import os
import time
import pandas as pd
from pathlib import Path
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium_core.waits import wait_and_send_keys, wait_for_element
from selenium_core.utils import formatar_inscricao
from selenium_core.logger import get_logger
from selenium_core.exceptions import DataValidationError
from selenium_core.metrics import ExecutionMetrics
from .certificate_updater import CertificateUpdater

logger = get_logger(__name__)


class CompanyProcessor:
    """Processes companies for certificate updates."""
    
    def __init__(self, driver: Chrome):
        """
        Initialize company processor.
        
        Args:
            driver: Chrome WebDriver instance
        """
        self.driver = driver
        self.updater = CertificateUpdater(driver)
    
    def process_from_csv(self, csv_path: str) -> None:
        """
        Process companies from CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Raises:
            DataValidationError: If CSV is invalid
        """
        logger.info(f"Loading companies from {csv_path}")
        
        # Load CSV
        companies_df = self._load_csv(csv_path)
        
        if companies_df.empty:
            raise DataValidationError("No companies found in CSV")
        
        total = len(companies_df)
        logger.info(f"Found {total} companies to process")
        
        # Initialize metrics
        metrics = ExecutionMetrics(total_items=total)
        
        # Process each company
        for idx, (_, company) in enumerate(companies_df.iterrows(), 1):
            start_time = time.time()
            
            try:
                self.process_company(company)
                duration = time.time() - start_time
                metrics.add_success(duration)
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.add_failure(duration)
                logger.error(f"Failed to process company {idx}: {e}")
            
            # Print progress every 5 companies
            if idx % 5 == 0 or idx == total:
                metrics.print_progress()
        
        logger.info("Processing completed")
        logger.info(f"Summary: {metrics.get_summary()}")
    
    def process_company(self, company: pd.Series) -> None:
        """
        Process a single company.
        
        Args:
            company: Company data from CSV row
        """
        # Validate and format inscription
        inscricao = formatar_inscricao(company['inscricao_federal'])
        
        if not inscricao or inscricao == 'Inscrição inválida':
            logger.warning(f"Invalid inscription for company: {company.get('nome', 'Unknown')}")
            return
        
        # Build certificate path
        certificate_path = self._build_certificate_path(company)
        
        if not os.path.exists(certificate_path):
            logger.warning(f"Certificate file not found: {certificate_path}")
            return
        
        password = str(company['senha'])
        
        logger.info(f"Processing: {company.get('nome', 'Unknown')} (Inscription: {inscricao})")
        
        # Search for company
        if self._search_company(inscricao):
            # Update certificate
            self.updater.update_certificate(inscricao, certificate_path, password)
        else:
            logger.warning(f"Company not found or is MEI: {inscricao}")
    
    def _load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load and validate CSV file."""
        if not Path(csv_path).exists():
            raise DataValidationError(f"CSV file not found: {csv_path}")
        
        try:
            df = pd.read_csv(
                csv_path,
                dtype={
                    "inscricao_federal": "string",
                    "nome": "string",
                    "caminho_raiz": "string",
                    "caminho_arquivo": "string",
                    "senha": "string",
                },
                encoding="utf-8",
                sep=","
            )
            return df
        except Exception as e:
            raise DataValidationError(f"Failed to load CSV: {e}") from e
    
    def _build_certificate_path(self, company: pd.Series) -> str:
        """Build full certificate file path."""
        if pd.isna(company.get('caminho_raiz')):
            return str(company['caminho_arquivo'])
        
        return os.path.join(
            company['caminho_raiz'],
            company['caminho_arquivo']
        )
    
    def _search_company(self, inscricao: str) -> bool:
        """
        Search for company by inscription.
        
        Args:
            inscricao: Company federal inscription
            
        Returns:
            True if company found, False otherwise
        """
        # Fill search field
        wait_and_send_keys(
            self.driver,
            By.XPATH,
            '//*[@placeholder="Nome/Insc. Federal"]',
            inscricao
        )
        
        time.sleep(1)
        
        # Check if company appears in results
        try:
            wait_for_element(
                self.driver,
                By.XPATH,
                '//*[@id="def-table"]/tbody/tr[1]/td[7]/a/span',
                timeout=10
            )
            return True
        except Exception:
            return False
