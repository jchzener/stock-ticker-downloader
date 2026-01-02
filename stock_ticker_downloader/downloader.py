from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ExchangeConfig:
    """Configuration for stock exchange data retrieval"""
    name: str
    api_params: Dict[str, str]

class StockTickerDownloader:
    """
    Optimized stock ticker downloader that fetches and processes stock data from NASDAQ API
    """
    def __init__(self, output_dir: str="active_tickers", user_agent: Optional[str]=None):

