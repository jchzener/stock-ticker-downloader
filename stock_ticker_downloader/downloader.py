import os
import json
import logging
from textwrap import indent
from typing import Dict, Optional
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NASDAQ_API_URL = os.getenv("NASDAQ_API_URL", "")


class StockTickerDownloader:
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

    def _create_dirs(self):
        for exchange in self.exchanges + ["all"]:
            (self.output_dir / exchange).mkdir(parents=True, exist_ok=True)

    def _fetch_data(self, exchange: str) -> Optional[Dict]:
        """
        Fetch stock data for a specific exchange.

        Args:
            exchange_name: Name of exchange ("nasdaq" or "nyse")

        Returns:
            JSON response data or None if request fails
        """
        try:
            params = {"tableonly": "true", "download": "true", "exchange": exchange}
            response = self.session.get(url=NASDAQ_API_URL, params=params, timeout=30)
            data = response.json()
            self.logger.info(
                f"Succesfully fetched {len(data.get('data', {}).get('rows', []))} tickers for {exchange}"
            )
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch data for {exchange}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response for {exchange}: {e}")
            return None

    def _save_files(self, exchange: str, data: Optional[Dict]):
        if data:
            exchange_dir = self.output_dir / exchange
            rows = data.get("data", {}).get("rows", [])
            tickers = [row.get("symbol") for row in rows]
            # saving
            (exchange_dir / f"{exchange}_full.json").write_text(
                json.dumps(rows, indent=2)
            )
            (exchange_dir / f"{exchange}_tickers.txt").write_text("\n".join(tickers))
            self.logger.info(
                f"Saved {len(tickers)} for {exchange} in {self.output_dir}"
            )

    def _process_exchange(self, exchange: str) -> bool:
        data = self._fetch_data(exchange)
        if data:
            self._save_files(exchange, data)
            return True
        else:
            return False

    def _combine_all(self):
        all_tickers = set()
        for ex in self.exchanges:
            file_name = self.output_dir / ex / f"{ex}_tickers.txt"
            if file_name.exists():
                all_tickers.update(file_name.read_text().strip().splitlines())

        (self.output_dir / "all" / "all_tickers.txt").write_text(
            "\n".join(sorted(all_tickers))
        )
        self.logger.info("Combined and saved {len(all_tickers)} unique tickers")

    def run(self, workers: int = 2) -> bool:
        self._create_dirs()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            success_count = sum(executor.map(self._process_exchange, self.exchanges))
        self.logger.info(f"Success: {success_count}/{len(self.exchanges)}")
        if success_count:
            self._combine_all()
            return True
        return False


def main():
    if StockTickerDownloader(output_dir).run():
        print(f"Success!")
    else:
        exit(1)


if __name__ == "__main__":
    output_dir = "active_tickers"
    main()
