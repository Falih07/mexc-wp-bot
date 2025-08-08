
import os, time, requests, math
from urllib.parse import urlencode
from utils import now_ms, sign_params

BASE = "https://api.mexc.com"  # Spot V3

API_KEY = os.getenv("MEXC_KEY", "")
API_SECRET = os.getenv("MEXC_SECRET", "").encode()

def _headers():
    return {"X-MEXC-APIKEY": API_KEY, "Content-Type": "application/json"}

def server_time():
    r = requests.get(f"{BASE}/api/v3/time", timeout=15)
    r.raise_for_status()
    return r.json().get("serverTime")

def exchange_info(symbol=None):
    params = {}
    if symbol:
        params["symbol"] = symbol
    r = requests.get(f"{BASE}/api/v3/exchangeInfo", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def ticker_price(symbol):
    r = requests.get(f"{BASE}/api/v3/ticker/price", params={"symbol": symbol}, timeout=15)
    r.raise_for_status()
    return float(r.json()["price"])

def klines(symbol, interval="5m", startTime=None, endTime=None, limit=1000):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if startTime is not None: params["startTime"] = startTime
    if endTime is not None: params["endTime"] = endTime
    r = requests.get(f"{BASE}/api/v3/klines", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def account_info():
    ts = now_ms()
    params = {"timestamp": ts, "recvWindow": 5000}
    params["signature"] = sign_params(params, API_SECRET)
    r = requests.get(f"{BASE}/api/v3/account", params=params, headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()

def place_order(symbol, side, type_, quantity=None, quoteOrderQty=None):
    ts = now_ms()
    params = {
        "symbol": symbol,
        "side": side,  # BUY / SELL
        "type": type_, # MARKET / LIMIT
        "timestamp": ts,
        "recvWindow": 5000,
    }
    if quantity is not None:
        params["quantity"] = f"{quantity:.12f}".rstrip('0').rstrip('.')
    if quoteOrderQty is not None:
        params["quoteOrderQty"] = f"{quoteOrderQty:.8f}".rstrip('0').rstrip('.')
    params["signature"] = sign_params(params, API_SECRET)
    r = requests.post(f"{BASE}/api/v3/order", params=params, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def cancel_all(symbol):
    ts = now_ms()
    params = {"symbol": symbol, "timestamp": ts, "recvWindow": 5000}
    params["signature"] = sign_params(params, API_SECRET)
    r = requests.delete(f"{BASE}/api/v3/openOrders", params=params, headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()

def filters_for_symbol(symbol):
    info = exchange_info(symbol)
    sym = None
    for s in info.get("symbols", []):
        if s.get("symbol") == symbol:
            sym = s; break
    if not sym: return {}
    out = {}
    for f in sym.get("filters", []):
        out[f.get("filterType")] = f
    return out
