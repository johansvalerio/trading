import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Optional
from config import API_BASE_URL, TIMEFRAME
import yfinance as yf

class ExchangeClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_historical_data(self, symbol: str, timeframe: str = TIMEFRAME, 
                          limit: int = 200) -> Optional[pd.DataFrame]:
        """Fetch historical candle data from exchange"""
        # Allow forcing a provider via environment, e.g. USE_PROVIDER=yfinance/coingecko/binance
        provider = os.getenv("USE_PROVIDER", "auto").lower()
        if provider == "yfinance":
            return self._fallback_historical_yf(symbol, timeframe, limit)
        if provider == "coingecko":
            return self._fallback_historical_coingecko(symbol, timeframe, limit)
        # Default flow: try Binance -> yfinance -> CoinGecko
        try:
            # Map timeframe to Binance format
            timeframe_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
                '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
            }
            
            if timeframe not in timeframe_map:
                print(f"[ERROR] Unsupported timeframe: {timeframe}")
                return None
            
            binance_timeframe = timeframe_map.get(timeframe, '1h')
            
            params = {
                'symbol': symbol,
                'interval': binance_timeframe,
                'limit': limit
            }
            
            # Try multiple Binance hosts to avoid geo blocks
            default_hosts = [
                "https://data-api.binance.vision/api/v3",  # public mirrored data host
                "https://api.binance.com/api/v3"
            ]
            # Allow override via env (comma-separated)
            env_hosts = os.getenv("BINANCE_BASE_URLS")
            hosts = [h.strip() for h in env_hosts.split(",") if h.strip()] if env_hosts else default_hosts

            # Set a simple User-Agent to avoid being blocked by some CDNs
            headers = {"User-Agent": "Mozilla/5.0 (compatible; TradingBot/1.0)"}

            last_error = None
            for host in hosts:
                url = f"{host}/klines"
                print(f"[DEBUG] Fetching data from {url} with params: {params}")
                try:
                    response = self.session.get(
                        url,
                        params=params,
                        timeout=30,
                        headers=headers
                    )
                    print(f"[DEBUG] Response status: {response.status_code} for host {host}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"[DEBUG] Received {len(data)} candles from {host}")
                        if not data:
                            last_error = "Empty response"
                            continue
                        df = pd.DataFrame(data, columns=[
                            'open_time', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                            'taker_buy_quote', 'ignore'
                        ])
                        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
                        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
                        for col in numeric_columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        df.set_index('open_time', inplace=True)
                        df = df.sort_index()
                        self.last_provider = "binance"
                        return df
                    else:
                        try:
                            body = response.text[:200]
                        except Exception:
                            body = "<no-body>"
                        last_error = f"Status {response.status_code} Body {body}"
                        print(f"[DEBUG] Binance host {host} failed: {last_error}")
                except Exception as e:
                    last_error = str(e)
                    print(f"[DEBUG] Exception calling {host}: {e}")

            print(f"[WARN] All Binance hosts failed. Last error: {last_error}")
            # Fallback to yfinance if all Binance hosts fail
            df = self._fallback_historical_yf(symbol, timeframe, limit)
            if df is not None and not df.empty:
                self.last_provider = "yfinance"
                return df
            # If yfinance also fails, try CoinGecko
            df = self._fallback_historical_coingecko(symbol, timeframe, limit)
            if df is not None and not df.empty:
                self.last_provider = "coingecko"
            return df
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching historical data from Binance: {e}")
            # Fallback to yfinance on network errors
            df = self._fallback_historical_yf(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
            return self._fallback_historical_coingecko(symbol, timeframe, limit)
        except Exception as e:
            print(f"Error processing historical data from Binance: {e}")
            df = self._fallback_historical_yf(symbol, timeframe, limit)
            if df is not None and not df.empty:
                return df
            return self._fallback_historical_coingecko(symbol, timeframe, limit)

    def _fallback_historical_yf(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fallback to yfinance when Binance API is unavailable."""
        try:
            # Map timeframe to yfinance intervals
            yf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '60m', '2h': '120m', '4h': '240m', '6h': '360m', '8h': '480m', '12h': '720m',
                '1d': '1d', '3d': '3d', '1w': '1wk', '1M': '1mo'
            }
            interval = yf_map.get(timeframe, '60m')

            # Convert crypto symbol to yfinance format, e.g., BTCUSDT -> BTC-USD
            yf_symbol = symbol
            if symbol.upper().endswith('USDT'):
                base = symbol.upper().replace('USDT', '')
                yf_symbol = f"{base}-USD"

            print(f"[FALLBACK] Fetching yfinance data for {yf_symbol} interval={interval} limit={limit}")

            # yfinance does not have a direct 'limit' parameter; we request a period covering at least 'limit' candles
            period_map = {
                '1m': '2d', '5m': '10d', '15m': '30d', '30m': '60d',
                '60m': '200d', '120m': '400d', '240m': '800d', '360m': '1000d', '480m': '1200d', '720m': '1500d',
                '1d': '2y', '3d': '5y', '1wk': '5y', '1mo': '10y'
            }
            period = period_map.get(interval, '200d')

            df = yf.download(yf_symbol, interval=interval, period=period, progress=False)
            if df is None or df.empty:
                print("[FALLBACK] yfinance returned empty DataFrame")
                return None

            # Keep only the last 'limit' rows
            df = df.tail(limit)

            # Standardize columns to match expected format
            df = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })

            required = ['open', 'high', 'low', 'close', 'volume']
            for col in required:
                if col not in df.columns:
                    print(f"[FALLBACK] Missing column in yfinance data: {col}, filling default")
                    # Ensure volume exists to avoid downstream division by zero
                    if col == 'volume':
                        df['volume'] = 1.0
                    else:
                        return None

            # Ensure numeric types
            for col in required:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Ensure index is datetime and sorted
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            df = df.sort_index()

            print(f"[FALLBACK] yfinance provided {len(df)} candles")
            return df
        except Exception as e:
            print(f"[FALLBACK] Error fetching yfinance data: {e}")
            return None

    def _fallback_historical_coingecko(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fallback to CoinGecko OHLC endpoint. Note: volume not provided; we set a default."""
        try:
            # Map symbol to CoinGecko coin id (support BTCUSDT -> bitcoin)
            coin_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum'
            }
            cg_id = None
            sym = symbol.upper()
            if sym.endswith('USDT'):
                base = sym[:-4]
                cg_id = coin_map.get(base, 'bitcoin')
            else:
                cg_id = coin_map.get(sym, 'bitcoin')

            # CoinGecko granularity is driven by 'days' and returns up to 300 candles depending on range.
            # Choose days so we get at least 'limit' candles for the timeframe.
            if timeframe in ['1h', '2h', '4h', '6h', '8h', '12h']:
                days = 14  # enough to cover ~200 hours
            elif timeframe in ['1d', '3d']:
                days = 365
            else:
                days = 30

            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc"
            vs_currency = 'usd'
            interval_map = {
                '1h': '1h', '2h': '1h', '4h': '4h', '6h': '4h', '8h': '4h', '12h': '4h',
                '1d': '1d', '3d': '1d'
            }
            # CoinGecko supports only 1, 4, and 24-hour data effectively via OHLC endpoint.
            cg_interval = interval_map.get(timeframe, '1h')

            params = { 'vs_currency': vs_currency, 'days': days }
            print(f"[FALLBACK-CG] Fetching CoinGecko OHLC for {cg_id} days={days}")
            r = requests.get(url, params=params, timeout=20)
            if r.status_code != 200:
                print(f"[FALLBACK-CG] CoinGecko error {r.status_code}: {r.text[:200]}")
                return None
            data = r.json()
            if not isinstance(data, list) or len(data) == 0:
                print("[FALLBACK-CG] Empty OHLC data")
                return None
            # Data rows: [timestamp, open, high, low, close]
            rows = []
            for row in data[-limit:]:
                try:
                    ts_ms, o, h, l, c = row
                    rows.append({
                        'open_time': pd.to_datetime(int(ts_ms), unit='ms'),
                        'open': float(o), 'high': float(h), 'low': float(l), 'close': float(c),
                        'volume': 1.0  # default volume
                    })
                except Exception:
                    continue
            if not rows:
                print("[FALLBACK-CG] No parsable rows")
                return None
            df = pd.DataFrame(rows)
            df.set_index('open_time', inplace=True)
            df = df.sort_index()
            print(f"[FALLBACK-CG] Provided {len(df)} candles")
            return df
        except Exception as e:
            print(f"[FALLBACK-CG] Exception: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price"""
        try:
            response = self.session.get(
                f"{self.base_url}/ticker/price",
                params={'symbol': symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            else:
                print(f"Error fetching current price: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None
    
    def get_24h_stats(self, symbol: str) -> Optional[dict]:
        """Get 24-hour statistics"""
        try:
            response = self.session.get(
                f"{self.base_url}/ticker/24hr",
                params={'symbol': symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price_change': float(data['priceChange']),
                    'price_change_percent': float(data['priceChangePercent']),
                    'weighted_avg_price': float(data['weightedAvgPrice']),
                    'prev_close_price': float(data['prevClosePrice']),
                    'last_price': float(data['lastPrice']),
                    'bid_price': float(data['bidPrice']),
                    'ask_price': float(data['askPrice']),
                    'volume': float(data['volume']),
                    'quote_volume': float(data['quoteVolume']),
                    'high_price': float(data['highPrice']),
                    'low_price': float(data['lowPrice'])
                }
            else:
                print(f"Error fetching 24h stats: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching 24h stats: {e}")
            return None
    
    def wait_for_rate_limit(self, delay: float = 1.0):
        """Wait to respect rate limits"""
        time.sleep(delay)

# Legacy function to maintain compatibility
def get_historical_data(symbol: str, timeframe: str = '1h', limit: int = 200) -> Optional[pd.DataFrame]:
    """Legacy function for backward compatibility"""
    client = ExchangeClient()
    return client.get_historical_data(symbol, timeframe, limit)