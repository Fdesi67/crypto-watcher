import os

# Coins to watch — BloFin uses "BASE-QUOTE" format
COINS = [
    "BTC-USDT",
    "ETH-USDT",
    "FARTCOIN-USDT",
    "RENDER-USDT",
    "SAHARA-USDT",
]

EMA_PERIOD = 200
CANDLE_BAR = "1H"          # 1H, 4H, 1D, 15m, etc.
CANDLES_TO_FETCH = 300     # fetch extra so EMA has time to warm up

POLL_INTERVAL_SECONDS = 60       # check every 1 minute

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_IDS: list[str] = os.environ["TELEGRAM_CHAT_ID"].split(",")

BLOFIN_BASE_URL = "https://openapi.blofin.com"
