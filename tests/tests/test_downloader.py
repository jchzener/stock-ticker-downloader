"""Tests for the stock ticker downloader."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from stock_ticker_downloader.downloader import StockTickerDownloader, ExchangeConfig
