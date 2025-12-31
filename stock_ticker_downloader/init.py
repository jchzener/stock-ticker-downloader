"""Stock Ticker Downloader package."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "jean@dpdil.tech"

from .downloader import StockTickerDownloader, ExchangeConfig

__all__ = ["StockTickerDownloader", "ExchangeConfig"]
