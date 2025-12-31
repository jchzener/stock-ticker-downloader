from dataclasses import dataclass
from typing import Dict

@dataclass
class ExchangeConfig:
    """Configuration for stock exchange data retrieval"""
    name: str
    api_params: Dict[str, str]

class StockTickerDownloader:
    """
    Optimized stock ticker downloader that fetches and processes stock data from NASDAQ API
    """
    def __init__(self):

