
# MEXC Spot Bot — Minimal (for WordPress.com free users)

**Tujuan:** bot trading spot MEXC berjalan otomatis TANPA hosting berbayar,
memakai **GitHub Actions** (interval tiap 5 menit) + Python. WordPress.com (gratis)
hanya dipakai sebagai halaman status/tautan, bukan eksekusi bot.

> ⚠️ Default: **paper-trading** (tidak mengirim order live). Aktifkan trading live di `config.yaml` dan pahami risikonya.

## Fitur
- Strategi plugin: SMA crossover, RSI reversal, MACD cross, Bollinger mean reversion, Donchian breakout.
- Backtest dari data candle MEXC (`/api/v3/klines`).
- Risk: ukuran tetap per trade (USDT), cek **MIN_NOTIONAL** & **LOT_SIZE**.
- Live runner via GitHub Actions schedule (`*/5 * * * *`).
- Log hasil ke `reports/` dan ringkasan `reports/summary.json`.
- (Opsional) kirim notifikasi Telegram (set token & chat id).

## Struktur
```
mexc-wp-bot/
  .github/workflows/trade.yml
  backtest.py
  live.py
  mexc_api.py
  strategies/
    __init__.py
    sma_crossover.py
    rsi.py
    macd.py
    bbands_mean_revert.py
    donchian_breakout.py
  utils.py
  config.yaml
  requirements.txt
  reports/
```

## Cara Pakai (langkah cepat)
1) **Buat repo GitHub** baru dan upload isi folder ini (atau unzip & push).
2) Di repo → **Settings → Secrets and variables → Actions → New repository secret**:
   - `MEXC_KEY` = API Key
   - `MEXC_SECRET` = API Secret
   - (opsional) `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
3) Di repo → **Settings → Actions → General → Workflow permissions** → Centang **Read and write permissions** (dibutuhkan untuk menyimpan log/summary ke repo).
4) Edit `config.yaml`:
   - `live_trading: false` (awal), `symbol: BTCUSDT`, `timeframe: 1m`/`5m`, `quote_size_usdt: 1.5` (>= 1 USDT sesuai min order sebagian besar pair USDT).
   - Pilih strategi di `enabled_strategies:`.
5) Jalankan **Backtest** manual: buka tab *Actions* → pilih workflow **Backtest** → **Run workflow** (atau lokal: `pip install -r requirements.txt && python backtest.py`).
6) Jika puas, aktifkan **Live Runner**:
   - Set `live_trading: true` di `config.yaml`.
   - Pastikan saldo cukup & paham risiko. Bot akan jalan tiap 5 menit via GitHub Actions.
7) **Integrasi WordPress.com (gratis):**
   - Tambah *Image Block* yang menunjuk ke file PNG ringkasan di GitHub (misal badge/chart yang bot buat di `reports/` bila Anda publish lewat GitHub Pages). WordPress gratis tidak mengizinkan JS/plugin custom.
   - Alternatif: tempel link ke file `reports/summary.json` pada GitHub.

## Catatan
- Jadwal GitHub Actions minimal **5 menit** (bukan realtime). Untuk interval 1 menit, pakai Cloudflare Workers (berlaku limit gratis).
- Default strategi jalan **paper-trade** dulu bersamaan; hanya strategi di `exec_strategy` yang mengeksekusi order live (kalau `live_trading=true`).

## Disclaimer
Kodenya edukasi—pakai risiko Anda sendiri. Selalu mulai sangat kecil.
