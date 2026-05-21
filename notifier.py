import requests
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {
            "chat_id": chat_id.strip(),
            "text": message,
            "parse_mode": "Markdown",
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
        except Exception as exc:
            print(f"[telegram] Failed to send to {chat_id}: {exc}")


def price_summary(states: dict) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"🕐 *Price Update — {now}*\n"]
    for symbol, state in states.items():
        position = "▲" if state.close > state.ema else "▼"
        pct = ((state.close - state.ema) / state.ema) * 100
        lines.append(f"{position} *{symbol}*: `${state.close:,.4f}` ({pct:+.2f}% vs EMA)")
    return "\n".join(lines)


def ema_cross_alert(symbol: str, direction: str, close: float, ema: float) -> str:
    if direction == "above":
        emoji = "🟢"
        label = "crossed ABOVE 200 EMA"
        signal = "Bullish signal"
    else:
        emoji = "🔴"
        label = "crossed BELOW 200 EMA"
        signal = "Bearish signal"

    pct_from_ema = ((close - ema) / ema) * 100

    return (
        f"{emoji} *{symbol} — {label}*\n"
        f"Price: `${close:,.4f}`\n"
        f"200 EMA: `${ema:,.4f}`\n"
        f"Distance: `{pct_from_ema:+.2f}%`\n"
        f"_{signal} on 1H chart_"
    )
