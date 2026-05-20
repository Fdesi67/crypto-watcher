import time
from dotenv import load_dotenv
load_dotenv()
from blofin import get_candle_state, CandleState
from notifier import send_telegram, ema_cross_alert, price_summary
from config import COINS, POLL_INTERVAL_SECONDS, EMA_PERIOD, CANDLE_BAR

SUMMARY_INTERVAL_SECONDS = 60 * 60 * 2  # 2 hours

# Track previous candle state per coin so we detect the crossover moment
_prev_state: dict[str, CandleState] = {}
_last_summary_time: float = 0


def check_crossover(state: CandleState) -> None:
    prev = _prev_state.get(state.symbol)

    # On first run, just store state without alerting
    if prev is None:
        position = "above" if state.close > state.ema else "below"
        print(f"  {state.symbol}: ${state.close:,.4f}  EMA={state.ema:,.4f}  (currently {position} EMA)")
        return

    was_above = prev.close > prev.ema
    is_above = state.close > state.ema

    if not was_above and is_above:
        # Crossed above
        msg = ema_cross_alert(state.symbol, "above", state.close, state.ema)
        send_telegram(msg)
        print(f"  [ALERT] {state.symbol} crossed ABOVE 200 EMA at ${state.close:,.4f}")
    elif was_above and not is_above:
        # Crossed below
        msg = ema_cross_alert(state.symbol, "below", state.close, state.ema)
        send_telegram(msg)
        print(f"  [ALERT] {state.symbol} crossed BELOW 200 EMA at ${state.close:,.4f}")
    else:
        position = "above" if is_above else "below"
        print(f"  {state.symbol}: ${state.close:,.4f}  EMA={state.ema:,.4f}  ({position})")


def main() -> None:
    print(f"[bot] Starting — watching {len(COINS)} coins on {CANDLE_BAR} {EMA_PERIOD} EMA")
    send_telegram(
        f"🤖 *Crypto EMA Watcher started*\n"
        f"Coins: {', '.join(COINS)}\n"
        f"Signal: {EMA_PERIOD} EMA crossover ({CANDLE_BAR} candles)"
    )

    while True:
        global _last_summary_time
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking prices...")
        for symbol in COINS:
            try:
                state = get_candle_state(symbol)
                check_crossover(state)
                _prev_state[symbol] = state
            except Exception as exc:
                print(f"  [ERROR] {symbol}: {exc}")

        if time.time() - _last_summary_time >= SUMMARY_INTERVAL_SECONDS and _prev_state:
            send_telegram(price_summary(_prev_state))
            _last_summary_time = time.time()
            print("  [summary] Sent 2-hour price update")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
