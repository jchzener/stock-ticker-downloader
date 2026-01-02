from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import requests


@dataclass
class ExchangeConfig:
    """Configuration for stock exchange data retrieval"""

    name: str
    api_params: Dict[str, str]


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
        self.exchanges = [
            ExchangeConfig(
                "nasdaq", {"exchange": "nasdaq", "limit": "5000", "offset": "0"}
            ),
            ExchangeConfig(
                "nyse", {"exchange": "nyse", "limit": "5000", "offset": "0"}
            ),
        ]

    def setup_logging(self):
        pass
