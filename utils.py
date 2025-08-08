
import time, hmac, hashlib
from urllib.parse import urlencode

def now_ms():
    return int(time.time()*1000)

def hmac_sha256(secret: bytes, query: str) -> str:
    return hmac.new(secret, query.encode(), hashlib.sha256).hexdigest()

def sign_params(params: dict, secret: bytes) -> str:
    qs = urlencode(params, doseq=True)
    return hmac_sha256(secret, qs)

def clamp_qty_step(qty, step):
    if step is None or step == 0:
        return qty
    # round down to step
    return (int(qty / step)) * step

def pct(a, b):
    if b == 0: return 0.0
    return (a - b) / b
