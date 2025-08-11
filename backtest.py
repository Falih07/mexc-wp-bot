
import os, math, time, json, yaml
import pandas as pd
from datetime import datetime, timedelta, timezone
from mexc_api import klines
from strategies import ALL

def to_ms(dt): return int(dt.timestamp()*1000)

def get_klines(symbol, interval, days):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    data = []
    cur = start
    while cur < end:
        batch = klines(symbol, interval=interval, startTime=to_ms(cur), endTime=to_ms(end), limit=1000)
        if not batch: break
        data += batch
        # move forward using last open time
        last_open_ms = batch[-1][0]
        cur = datetime.fromtimestamp(last_open_ms/1000, tz=timezone.utc) + timedelta(milliseconds=1)
        if len(batch) < 1000:
            break
        time.sleep(0.2)
    cols = ["open_time","open","high","low","close","volume","close_time","quote_volume"]
    df = pd.DataFrame(data, columns=cols)
    for c in ["open","high","low","close","volume","quote_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["dt"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df

def run_strategy(df, strat_cls):
    s = strat_cls()
    out = s.generate(df)
    out["ret"] = out["close"].pct_change()
    out["pos"] = out["signal"].shift(1).fillna(0)
    out["strategy_ret"] = out["pos"] * out["ret"]
    equity = (1 + out["strategy_ret"]).cumprod()
    return out, equity

def main():
    cfg = yaml.safe_load(open("config.yaml","r"))
    symbol = cfg["symbol"]; interval = cfg["timeframe"]; days = cfg["backtest"]["lookback_days"]
    df = get_klines(symbol, interval, days)
    results = {}
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    for name, strat in ALL.items():
        out, equity = run_strategy(df, strat)
        final = float(equity.iloc[-1]) if len(equity) else 1.0
        results[name] = {
            "final_equity": final,
            "cum_return_pct": round((final-1)*100, 2),
            "last_signal": int(out["signal"].iloc[-1]) if len(out) else 0
        }
        out[["dt","close","signal"]].to_csv(os.path.join(reports_dir, f"{name}_signals.csv"), index=False)

    summary = {
        "symbol": symbol,
        "interval": interval,
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "results": results
    }
    with open(os.path.join(reports_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
