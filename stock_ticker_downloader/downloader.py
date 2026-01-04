from dataclasses import dataclass
import json
import logging
from logging import handlers
from os import mkdir
from pathlib import Path
from typing import Dict, Optional
import requests


class StockTickerDownloader:
    """
    Optimized stock ticker downloader that fetches and processes stock data from NASDAQ API
    """

    def __init__(
        self, output_dir: str = "active_tickers", user_agent: Optional[str] = None
    ):
        """
        Initialized the downloader with output directory and user agent

        Args:
            - output_dir (str): Base directory for output files in the same location the routine is being run
            - user_agent (Optional[str]): Custom user agent string for API requests
        """
        self.output_dir = Path(output_dir)
        self.session = requests.Session()

        default_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        self.session.headers.update(
            {
                "User-Agent": user_agent or default_user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://www.nasdaq.com/",
            }
        )
        self.setup_logging()

        # configure NYSE and NASDAQ exchange parameters, limit high to get all tickers
        self.exchanges = ["nasdaq", "nyse"]

    def setup_logging(self):
        """Configure logging for the downloader"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("stock_downloader.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def create_directories(self) -> None:
        """Create output directories for each exchange and combined data"""
        try:
            for exchange in self.exchanges:
                (self.output_dir / exchange).mkdir(parents=True, exist_ok=True)
                (self.output_dir / "all").mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created output directories under {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create directories: {e}")
            raise

    def fetch_exchange_data(self, exchange_name: str) -> Optional[Dict]:
        """
        Fetch stock data for a specific exchange.

        Args:
            exchange_name: Name of exchange ("nasdaq" or "nyse")

        Returns:
            JSON response data or None if request fails
        """
        try:
            # Prepare API parameters
            params = {
                "tableonly": "true",
                "download": "true",
                "exchange": exchange_name,
            }

            self.logger.info(f"Fetching data for {exchange_name} with params: {params}")

            # Make API request
            response = self.session.get(
                "https://api.nasdaq.com/api/screener/stocks", params=params, timeout=30
            )
            response.raise_for_status()  # Raises an HTTPError for bad responses

            data = response.json()
            self.logger.info(
                f"Successfully fetched {len(data.get('data', {}).get('rows', []))} "
                f"tickers for {exchange_name}"
            )
            return data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch data for {exchange_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response for {exchange_name}: {e}")
            return None
