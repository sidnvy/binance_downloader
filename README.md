# Binance Downloader

## Overview
Binance Downloader is a Python package for efficiently downloading cryptocurrency data from the Binance API. It supports downloading various types of data including trading klines, aggregate trades, ticker data, and more, with a focus on futures market data.

## Features
- Download data from Binance Futures market.
- Supports various data types like klines, aggregate trades, book tickers, etc.
- Parallel downloading for faster data retrieval.
- Progress bar to track download status.
- Easy to use with a simple Python API.

## Installation
To install Binance Downloader, you will need Python 3.10 or later. The package can be installed via pip. Run the following command:
```bash
pip install binance_history_downloader
```

## Usage
Here is a basic example of how to use Binance Downloader:

```python
from binance_history_downloader import download
from binance_history_downloader import DataType

# Example: Downloading premium index klines for SOLUSDT
data, errors = download('SOLUSDT', DataType.PREMIUM_INDEX_KLINES, '2023-01-01', '2023-01-31')
# Example usage
# df, errors  = download('SOLUSDT', DataType.PREMIUM_INDEX_KLINES', '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.INDEX_PRICE_KLINES, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.MARK_PRICE_KLINES, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.KLINES, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.AGG_TRADES, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.BOOK_TICKER, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.METRICS, '2023-10-20', '2023-11-16')
# df = download('SOLUSDT', DataType.LIQUIDATION_SNAPSHOT, '2023-10-20', '2023-11-16')


# Check for errors
if errors:
    print("Errors occurred:", errors)

# Work with the data
print(data.head())
```

## Requirements
- Python 3.10+
- pandas
- tqdm

## Contributing
Contributions to Binance Downloader are welcome! Please read our contributing guidelines for details on how to contribute.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

