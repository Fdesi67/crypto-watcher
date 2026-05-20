import requests
from dataclasses import dataclass
from config import BLOFIN_BASE_URL, CANDLES_TO_FETCH, EMA_PERIOD, CANDLE_BAR


@dataclass
class CandleState:
    symbol: str
    close: float       # latest closed candle close price
    prev_close: float  # previous candle close price
    ema: float         # 200 EMA on latest candle
    prev_ema: float    # 200 EMA on previous candle


def _calculate_ema(prices: list[float], period: int) -> list[float]:
    """Exponential moving average over a list of prices."""
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices, got {len(prices)}")
    k = 2.0 / (period + 1)
    # seed with SMA of first `period` values so the EMA warms up properly
    sma = sum(prices[:period]) / period
    ema_values = [sma]
    for price in prices[period:]:
        ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values


def get_candle_state(symbol: str) -> CandleState:
    """
    Fetch recent candles from BloFin and return the current + previous
    close price alongside the 200 EMA for each, for crossover detection.
    """
    resp = requests.get(
        f"{BLOFIN_BASE_URL}/api/v1/market/candles",
        params={"instId": symbol, "bar": CANDLE_BAR, "limit": CANDLES_TO_FETCH},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != "0" or not data.get("data"):
        raise ValueError(f"Unexpected BloFin response for {symbol}: {data}")

    # BloFin returns candles newest-first: [ts, open, high, low, close, vol, volCcy]
    # Reverse so index 0 is the oldest candle
    rows = list(reversed(data["data"]))

    # Skip the last (in-progress) candle — use only fully closed candles
    rows = rows[:-1]

    closes = [float(row[4]) for row in rows]

    if len(closes) < EMA_PERIOD + 2:
        raise ValueError(f"{symbol}: not enough candles ({len(closes)}) to compute {EMA_PERIOD} EMA")

    ema_series = _calculate_ema(closes, EMA_PERIOD)

    # ema_series[i] corresponds to closes[EMA_PERIOD - 1 + i]
    curr_ema = ema_series[-1]
    prev_ema = ema_series[-2]
    curr_close = closes[-1]
    prev_close = closes[-2]

    return CandleState(
        symbol=symbol,
        close=curr_close,
        prev_close=prev_close,
        ema=curr_ema,
        prev_ema=prev_ema,
    )
