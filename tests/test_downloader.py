"""Tests for the stock ticker downloader."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import os

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
import sys

sys.path.insert(0, str(project_root))

from stock_ticker_downloader.downloader import StockTickerDownloader


class TestStockTickerDownloader:

    def test_downloader_initialization(self):
        """Test downloader initialization."""
        downloader = StockTickerDownloader(output_dir="test_output")
        assert downloader.output_dir.name == "test_output"
        assert downloader.session is not None
        assert len(downloader.exchanges) == 2  # NASDAQ and NYSE only

        # Test with custom user agent
        custom_ua = "TestAgent/1.0"
        downloader_custom = StockTickerDownloader(user_agent=custom_ua)
        assert downloader_custom.session.headers["User-Agent"] == custom_ua

    @patch("stock_ticker_downloader.downloader.requests.Session.get")
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "rows": [
                    {"symbol": "AAPL", "name": "Apple Inc."},
                    {"symbol": "MSFT", "name": "Microsoft Corp."},
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        downloader = StockTickerDownloader()
        result = downloader._fetch_data("nasdaq")

        # Assertions
        assert result == mock_response.json.return_value
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "nasdaq" in kwargs.get("params", {}).values()

    @patch("stock_ticker_downloader.downloader.requests.Session.get")
    def test_fetch_data_failure(self, mock_get):
        """Test data fetching failure."""
        # Mock exception
        mock_get.side_effect = Exception("Network Error")

        downloader = StockTickerDownloader()
        result = downloader._fetch_data("nasdaq")

        # Assertion
        assert result == {}

    def test_create_dirs(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_create_dirs"
            downloader = StockTickerDownloader(output_dir=test_dir.name)

            # Call the method
            downloader._create_dirs()

            # Assertions
            for exchange in downloader.exchanges + ["all"]:
                assert (test_dir / exchange).is_dir()

    def test_save_files(self):
        """Test saving exchange data to files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_save_files"
            exchange_name = "test_exchange"
            test_exchange_dir = test_dir / exchange_name

            downloader = StockTickerDownloader(output_dir=test_dir.name)
            mock_data = {
                "data": {
                    "rows": [
                        {"symbol": "TEST1", "name": "Test Company 1"},
                        {"symbol": "TEST2", "name": "Test Company 2"},
                    ]
                }
            }

            # Call the method
            downloader._save_files(exchange_name, mock_data)

            # Assertions
            assert (test_exchange_dir / f"{exchange_name}_full.json").exists()
            assert (test_exchange_dir / f"{exchange_name}_tickers.json").exists()
            assert (test_exchange_dir / f"{exchange_name}_tickers.txt").exists()

            # Check content of the text file (most important for user)
            with open(test_exchange_dir / f"{exchange_name}_tickers.txt", "r") as f:
                content = f.read().strip()
                assert "TEST1" in content
                assert "TEST2" in content
                assert "\n" in content  # Should be one per line

    @patch.object(StockTickerDownloader, "_fetch_data")
    @patch.object(StockTickerDownloader, "_save_files")
    def test_process_exchange_success(self, mock_save, mock_fetch):
        """Test processing an exchange successfully."""
        mock_fetch.return_value = {"data": {"rows": [{"symbol": "TEST"}]}}
        mock_save.return_value = None  # _save_files returns None implicitly

        downloader = StockTickerDownloader()
        result = downloader._process_exchange("test_exchange")

        assert result is True
        mock_fetch.assert_called_once_with("test_exchange")
        mock_save.assert_called_once()

    @patch.object(StockTickerDownloader, "_fetch_data")
    def test_process_exchange_failure(self, mock_fetch):
        """Test processing an exchange failing."""
        mock_fetch.return_value = {}  # Simulate failure in _fetch_data

        downloader = StockTickerDownloader()
        result = downloader._process_exchange("test_exchange")

        assert result is False
        mock_fetch.assert_called_once_with("test_exchange")

    def test_combine_all(self):
        """Test combining all tickers from different exchanges."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_combine"
            downloader = StockTickerDownloader(output_dir=test_dir.name)

            # Create mock ticker files
            nasdaq_dir = test_dir / "nasdaq"
            nyse_dir = test_dir / "nyse"
            nasdaq_dir.mkdir(parents=True)
            nyse_dir.mkdir(parents=True)

            # Write mock data (including duplicates)
            nasdaq_symbols = ["AAPL", "GOOGL", "MSFT"]
            nyse_symbols = ["MSFT", "TSLA", "AAPL"]  # Duplicates with NASDAQ

            (nasdaq_dir / "nasdaq_tickers.txt").write_text("\n".join(nasdaq_symbols))
            (nyse_dir / "nyse_tickers.txt").write_text("\n".join(nyse_symbols))

            # Call the method
            downloader._combine_all()

            # Assertions
            all_file_path = test_dir / "all" / "all_tickers.txt"
            assert all_file_path.exists()

            # Read and verify combined content
            combined_content = all_file_path.read_text().strip()
            combined_symbols = set(
                combined_content.split("\n")
            )  # Use set for uniqueness

            expected_symbols = {"AAPL", "GOOGL", "MSFT", "TSLA"}
            assert combined_symbols == expected_symbols
            # Check if it's sorted (the code sorts)
            lines = combined_content.split("\n")
            assert lines == sorted(lines)

    @patch.object(StockTickerDownloader, "_create_dirs")
    @patch.object(StockTickerDownloader, "_process_exchange")
    @patch.object(StockTickerDownloader, "_combine_all")
    def test_run_success(self, mock_combine, mock_process, mock_create):
        """Test successful run execution."""
        mock_process.return_value = True  # Simulate success for all exchanges

        downloader = StockTickerDownloader()
        result = downloader.run(workers=1)  # Use 1 worker for simpler testing

        assert result is True
        mock_create.assert_called_once()
        mock_combine.assert_called_once()
        assert mock_process.call_count == len(downloader.exchanges)

    @patch.object(StockTickerDownloader, "_create_dirs")
    @patch.object(StockTickerDownloader, "_process_exchange")
    @patch.object(StockTickerDownloader, "_combine_all")
    def test_run_failure(self, mock_combine, mock_process, mock_create):
        """Test run execution failure (no successful exchanges)."""
        mock_process.return_value = False  # Simulate failure for all exchanges

        downloader = StockTickerDownloader()
        result = downloader.run(workers=1)  # Use 1 worker for simpler testing

        assert result is False
        mock_create.assert_called_once()
        mock_combine.assert_not_called()  # Should not be called if no successes
        assert mock_process.call_count == len(downloader.exchanges)
