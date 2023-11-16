import concurrent.futures
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Tuple, Union

import pandas as pd
from tqdm import tqdm

base_url = "https://data.binance.vision/data"


class DataType(Enum):
    PREMIUM_INDEX_KLINES = "premiumIndexKlines"
    INDEX_PRICE_KLINES = "indexPriceKlines"
    MARK_PRICE_KLINES = "markPriceKlines"
    KLINES = "klines"
    TRADES = "trades"
    AGG_TRADES = "aggTrades"
    BOOK_TICKER = "bookTicker"
    METRICS = "metrics"
    LIQUIDATION_SNAPSHOT = "liquidationSnapshot"


def build_url(
    market: str,
    datatype: str,
    year: str,
    month: str,
    day: str = None,
    market_type: str = "futures",
) -> str:
    """Constructs the URL for the given parameters."""
    url_path = "daily" if day else "monthly"
    date_part = f"{year}-{month}" + (f"-{day}" if day else "")
    if market_type == "spot":
        market_base_url = base_url + "/spot"
    else:
        market_base_url = base_url + "/futures/um"
    if datatype.endswith("lines"):
        time_frame = "1m"
        return f"{market_base_url}/{url_path}/{datatype}/{market}/{time_frame}/{market}-{time_frame}-{date_part}.zip"
    return f"{market_base_url}/{url_path}/{datatype}/{market}/{market}-{datatype}-{date_part}.zip"


def get_timestamp_field(datatype: DataType) -> str:
    """Returns the appropriate timestamp field based on the datatype."""
    if datatype in [
        DataType.PREMIUM_INDEX_KLINES,
        DataType.INDEX_PRICE_KLINES,
        DataType.MARK_PRICE_KLINES,
        DataType.KLINES,
    ]:
        return "open_time"
    elif datatype == DataType.METRICS:
        return "create_time"
    elif datatype == DataType.BOOK_TICKER:
        return "event_time"
    elif datatype in [DataType.LIQUIDATION_SNAPSHOT, DataType.TRADES]:
        return "time"
    else:
        return "transact_time"


def download_data(url: str, datatype: DataType) -> Union[pd.DataFrame, str]:
    """Downloads data from the given URL and returns a DataFrame or an error message."""
    try:
        df = pd.read_csv(url, compression="zip")
        time_field = get_timestamp_field(datatype)
        df[time_field] = pd.to_datetime(
            df[time_field], unit="ms" if datatype != DataType.METRICS else None
        )
        return df
    except Exception as e:
        return f"Failed to download data from {url}: {e}"


def download(
    market: str,
    datatype: DataType,
    start_date: str,
    end_date: str,
    market_type: str = "futures",
) -> Tuple[pd.DataFrame, List[str]]:
    """Downloads data for the given market and datatype within the specified date range."""
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if not isinstance(datatype, DataType):
        raise ValueError("Invalid datatype. Please use a value from DataType enum.")

    urls_to_download = generate_download_urls(
        market, datatype, start_date, end_date, market_type
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            tqdm(
                executor.map(
                    lambda url: download_data(url, datatype), urls_to_download
                ),
                total=len(urls_to_download),
            )
        )

    return process_download_results(
        results, get_timestamp_field(datatype), start_date, end_date
    )


def generate_download_urls(
    market: str,
    datatype: DataType,
    start_date: datetime,
    end_date: datetime,
    market_type: str = "futures",
) -> List[str]:
    """Generates a list of URLs to download based on the given parameters."""
    urls_to_download = []
    # start_month = start_date.replace(day=1)
    # end_month = end_date.replace(day=1)
    # current_month_start = current_utc_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_utc_date = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # if datatype not in [DataType.LIQUIDATION_SNAPSHOT, DataType.METRICS]:
    #     months_to_download = pd.date_range(start=start_month, end=min(end_month, current_month_start - pd.offsets.MonthBegin(1)), freq='MS')
    #     urls_to_download.extend([build_url(market, datatype.value, month.strftime('%Y'), month.strftime('%m'), market_type=market_type) for month in months_to_download])
    #
    # if current_month_start <= end_date or datatype in [DataType.LIQUIDATION_SNAPSHOT, DataType.METRICS]:
    #     start = start_date if datatype in [DataType.LIQUIDATION_SNAPSHOT, DataType.METRICS] else max(start_date, current_month_start)
    #     daily_range = pd.date_range(start=start, end=end_date, freq='D')
    #     urls_to_download.extend([build_url(market, datatype.value, day.strftime('%Y'), day.strftime('%m'), day.strftime('%d'), market_type) for day in daily_range])

    # start = start_date if datatype in [DataType.LIQUIDATION_SNAPSHOT, DataType.METRICS] else max(start_date, current_month_start)
    daily_range = pd.date_range(
        start=start_date,
        end=min(current_utc_date - timedelta(days=1), end_date),
        freq="D",
    )
    urls_to_download.extend(
        [
            build_url(
                market,
                datatype.value,
                day.strftime("%Y"),
                day.strftime("%m"),
                day.strftime("%d"),
                market_type,
            )
            for day in daily_range
        ]
    )
    return urls_to_download


def process_download_results(
    results: List[Union[pd.DataFrame, str]],
    time_field: str,
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    """Processes the results of the downloads, aggregating data and errors."""
    all_data = pd.DataFrame()
    errors = []

    for result in results:
        if isinstance(result, pd.DataFrame):
            all_data = pd.concat([all_data, result])
        else:
            errors.append(result)

    all_data.set_index(time_field, inplace=True)
    all_data = all_data[start_date:end_date]
    return all_data, errors


# Example usage
# df, errors = download('spot', 'SOLUSDT', DataType.PREMIUM_INDEX_KLINES, '2023-01-01', '2023-01-31')
