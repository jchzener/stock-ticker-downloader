import json
import logging
from typing import Optional
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class StockTickersDownloader:
    """
    Download currently listed stock tickers on NASDAQ and NYSE
    Data is from 'https://api.nasdaq.com/api/screener/stocks'
    """

    def __init__(
        self, output_dir: str = "active_tickers", user_agent: Optional[str] = None
    ):
        self.output_dir = Path(output_dir)

        # Headers configuration
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.nasdaq.com/",
            }
        )
        # exchanges
        self.exchanges = ["nasdaq", "nyse"]

        # logging
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.Logger(__name__)
