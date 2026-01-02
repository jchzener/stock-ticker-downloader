"""Tests for the stock ticker downloader."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from stock_ticker_downloader.downloader import StockTickerDownloader, ExchangeConfig


def test_exchange_config():
    """Test ExchangeConfig dataclass."""
    config = ExchangeConfig("test", {"exchange": "test", "limit": "25"})
    assert config.name == "test"
    assert config.api_params == {"exchange": "test", "limit": "25"}


def test_downloader_initialization():
    """Test downloader initialization."""
    downloader = StockTickerDownloader(output_dir="test_output")
    assert downloader.output_dir.name == "test_output"
    assert downloader.session is not None
    assert len(downloader.exchanges) == 2  # NASDAQ and NYSE only
