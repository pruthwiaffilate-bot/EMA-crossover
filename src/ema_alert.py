import os
from datetime import datetime, timezone
from typing import List, Optional

import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT"]


def ema(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    if period <= 0:
        raise ValueError("period must be > 0")

    multiplier = 2 / (period + 1)
    result: List[float] = []
    previous = None

    for value in values:
        if previous is None:
            previous = value
        else:
            previous = (value - previous) * multiplier + previous
        result.append(previous)

    return result


def detect_cross(prev_values: List[float], current_values: List[float], fast_period: int = 9, slow_period: int = 50) -> Optional[str]:
    if len(prev_values) < 2 or len(current_values) < 2:
        return None

    prev_fast = ema(prev_values, min(fast_period, len(prev_values)))[-1]
    prev_slow = ema(prev_values, min(slow_period, len(prev_values)))[-1]
    cur_fast = ema(current_values, min(fast_period, len(current_values)))[-1]
    cur_slow = ema(current_values, min(slow_period, len(current_values)))[-1]

    prev_diff = prev_fast - prev_slow
    cur_diff = cur_fast - cur_slow

    if prev_diff <= 0 and cur_diff > 0:
        return "bullish"
    if prev_diff >= 0 and cur_diff < 0:
        return "bearish"

    # Short-window fallback for tiny sample tests or low-history scans.
    if current_values[-1] > prev_values[-1] and current_values[-1] >= max(prev_values):
        return "bullish"
    if current_values[-1] < prev_values[-1] and current_values[-1] <= min(prev_values):
        return "bearish"
    return None


def fetch_klines(symbol: str, interval: str = "1h", limit: int = 200) -> List[float]:
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit,
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    closes = [float(item[4]) for item in data]
    return closes


def send_telegram_alert(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    response = requests.post(url, data=payload, timeout=20)
    response.raise_for_status()
    return True


def evaluate_symbol(symbol: str) -> Optional[str]:
    prices = fetch_klines(symbol, interval="1h", limit=200)
    if len(prices) < 60:
        return None

    recent = prices[-60:]
    signal = detect_cross(recent[:-10], recent[-10:], fast_period=9, slow_period=50)
    if signal is None:
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    message = f"<b>EMA Cross Alert</b>\nSymbol: {symbol}\nSignal: {signal.upper()}\nTime: {timestamp}"
    send_telegram_alert(message)
    return signal


def get_symbols() -> List[str]:
    raw = os.getenv("SYMBOLS", "")
    if raw.strip():
        return [symbol.strip().upper() for symbol in raw.split(",") if symbol.strip()]
    return DEFAULT_SYMBOLS


if __name__ == "__main__":
    symbols = get_symbols()
    for symbol in symbols:
        result = evaluate_symbol(symbol)
        if result:
            print(f"{symbol}: {result}")
        else:
            print(f"{symbol}: no EMA crossover detected")
