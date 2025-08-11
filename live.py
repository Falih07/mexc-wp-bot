
import os, time, json, yaml, math, requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from mexc_api import ticker_price, place_order, filters_for_symbol, klines
from strategies import ALL

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def tg(msg: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: 
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": msg[:3900]} , timeout=10)
    except Exception:
        pass

def load_cfg():
    return yaml.safe_load(open("config.yaml","r"))

def lot_filters(symbol):
    f = filters_for_symbol(symbol)
    lot = f.get("LOT_SIZE", {})
    notional = f.get("MIN_NOTIONAL", {})
    step = float(lot.get("stepSize", "0.00000001"))
    min_qty = float(lot.get("minQty","0.0"))
    min_notional = float(notional.get("minNotional","1.0"))
    return step, min_qty, min_notional

def last_signal(symbol, interval, strat_cls):
    data = klines(symbol, interval=interval, limit=200)
    cols = ["open_time","open","high","low","close","volume","close_time","quote_volume"]
    df = pd.DataFrame(data, columns=cols)
    for c in ["open","high","low","close","volume","quote_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    s = strat_cls().generate(df)
    return int(s["signal"].iloc[-1])

def compute_qty(symbol, quote_usdt, price, step, min_qty, min_notional):
    # quantity from quote amount, respect min notional & lot step
    if price <= 0: return 0.0
    qty = quote_usdt / price
    # round down to step
    if step > 0:
        qty = math.floor(qty/step)*step
    if qty < min_qty:
        return 0.0
    if qty*price < min_notional:
        return 0.0
    return float(qty)

def main():
    cfg = load_cfg()
    symbol = cfg["symbol"]; interval = cfg["timeframe"]
    quote_usdt = float(cfg["quote_size_usdt"])
    live = bool(cfg["live_trading"])
    exec_strategy = cfg.get("exec_strategy", "sma_crossover")
    enabled = cfg.get("enabled_strategies", [])

    # Evaluate signals for all enabled strategies (paper log)
    paper = {}
    for name in enabled:
        strat_cls = ALL[name]
        sig = last_signal(symbol, interval, strat_cls)
        paper[name] = sig

    # Only one strategy is allowed to trade live
    sig_live = paper.get(exec_strategy, 0)

    price = ticker_price(symbol)
    step, min_qty, min_notional = lot_filters(symbol)

    action = "HOLD"
    if sig_live == 1:
        action = "BUY"
    elif sig_live == -1:
        action = "SELL"

    placed = None
    if live and action in ("BUY","SELL"):
        qty = compute_qty(symbol, quote_usdt, price, step, min_qty, min_notional)
        if qty > 0:
            placed = place_order(symbol, "BUY" if action=="BUY" else "SELL", "MARKET", quantity=qty)
        else:
            tg(f"[{symbol}] Gagal hitung qty (min_notional/step). price={price}, step={step}, min_qty={min_qty}, min_notional={min_notional}")

    summary = {
        "ts": datetime.utcnow().isoformat()+"Z",
        "symbol": symbol,
        "price": price,
        "interval": interval,
        "paper_signals": paper,
        "exec_strategy": exec_strategy,
        "live": live,
        "action": action,
        "order": placed or {}
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json","w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    tg(f"[{symbol}] price={price} | signals={paper} | exec={exec_strategy} -> {action} | live={live}")

if __name__ == "__main__":
    main()
