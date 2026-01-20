"""Tests for the stock ticker downloader."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent  # Adjust based on actual structure
sys.path.insert(0, str(project_root))


from stock_ticker_downloader.downloader import StockTickerDownloader


def test_downloader_initialization():
    """Test downloader initialization."""
    downloader = StockTickerDownloader(output_dir="test_output")
    assert downloader.output_dir.name == "test_output"
    assert downloader.session is not None
    assert len(downloader.exchanges) == 2  # NASDAQ and NYSE only
