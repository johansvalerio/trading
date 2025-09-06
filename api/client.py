import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Optional
from config import API_BASE_URL, TIMEFRAME

class ExchangeClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_historical_data(self, symbol: str, timeframe: str = TIMEFRAME, 
                          limit: int = 200) -> Optional[pd.DataFrame]:
        """Fetch historical candle data from exchange"""
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
            
            url = f"{self.base_url}/klines"
            print(f"[DEBUG] Fetching data from {url} with params: {params}")
            
            response = self.session.get(
                url,
                params=params,
                timeout=30
            )
            
            print(f"[DEBUG] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] Received {len(data)} candles")
                
                if not data:
                    print("[ERROR] Empty response data from exchange")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(data, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # Convert types
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
                
                numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Set timestamp as index
                df.set_index('open_time', inplace=True)
                
                # Sort by timestamp
                df = df.sort_index()
                
                return df
            else:
                print(f"Error fetching data: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching historical data: {e}")
            return None
        except Exception as e:
            print(f"Error processing historical data: {e}")
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