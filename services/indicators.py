import pandas as pd
import numpy as np
from typing import Tuple

class TechnicalIndicators:
    
    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI (Relative Strength Index)"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        return df
    
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std)
        df['bb_high'] = df['bb_upper']
        df['bb_low'] = df['bb_lower']
        return df
    
    @staticmethod
    def add_sma(df: pd.DataFrame, periods: list = [20, 50]) -> pd.DataFrame:
        """Calculate Simple Moving Averages"""
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ADX (Average Directional Index)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = abs(minus_dm)
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(window=period).mean()
        
        return df
    
    @staticmethod
    def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate ATR (Average True Range)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        df['atr'] = tr.rolling(window=period).mean()
        return df
    
    @staticmethod
    def add_volume_indicators(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        df['volume_ma'] = df['volume'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def add_support_resistance(df: pd.DataFrame, window: int = 50) -> pd.DataFrame:
        """Calculate support and resistance levels"""
        df['support'] = df['low'].rolling(window=window).min()
        df['resistance'] = df['high'].rolling(window=window).max()
        return df
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame, 
                          rsi_period: int = 14,
                          macd_fast: int = 12,
                          macd_slow: int = 26,
                          macd_signal: int = 9,
                          bb_period: int = 20,
                          bb_std: int = 2,
                          adx_period: int = 14,
                          atr_period: int = 14,
                          sma_periods: list = None) -> pd.DataFrame:
        """Add all technical indicators to the dataframe"""
        if sma_periods is None:
            sma_periods = [20, 50]
            
        df = TechnicalIndicators.add_rsi(df, rsi_period)
        df = TechnicalIndicators.add_macd(df, macd_fast, macd_slow, macd_signal)
        df = TechnicalIndicators.add_bollinger_bands(df, bb_period, bb_std)
        df = TechnicalIndicators.add_sma(df, sma_periods)
        df = TechnicalIndicators.add_adx(df, adx_period)
        df = TechnicalIndicators.add_atr(df, atr_period)
        df = TechnicalIndicators.add_volume_indicators(df)
        df = TechnicalIndicators.add_support_resistance(df)
        
        return df

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function to maintain compatibility with original app.py"""
    return TechnicalIndicators.add_all_indicators(df)

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for machine learning model"""
    features = pd.DataFrame()
    
    # Price-based features
    features['price_change'] = df['close'].pct_change()
    features['price_range'] = (df['high'] - df['low']) / df['close']
    features['price_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    # Technical indicator features
    features['rsi_normalized'] = df['rsi'] / 100
    features['macd_signal_diff'] = df['macd'] - df['macd_signal']
    features['adx_normalized'] = df['adx'] / 100
    features['atr_normalized'] = df['atr'] / df['close']
    
    # Moving average features
    features['sma_ratio'] = df['sma_20'] / df['sma_50']
    features['price_sma20_ratio'] = df['close'] / df['sma_20']
    
    # Volume features
    features['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # Support/resistance features
    features['support_distance'] = (df['close'] - df['support']) / df['close']
    features['resistance_distance'] = (df['resistance'] - df['close']) / df['close']
    
    return features.dropna()