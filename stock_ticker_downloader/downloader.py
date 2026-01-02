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
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0"
            }
        )
        self.setup_logging()

        # configure NYSE and NASDAQ exchange parameters
        self.exchanges = [
            ExchangeConfig(
                "nasdaq", {"exchange": "nasdaq", "limit": "3000", "offset": "0"}
            ),
            ExchangeConfig(
                "nyse", {"exchange": "nyse", "limit": "3000", "offset": "0"}
            ),
        ]

    def setup_logging(self):
        pass
