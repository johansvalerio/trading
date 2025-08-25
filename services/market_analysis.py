import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from config import (
    SIDEWAYS_ATR_THRESHOLD, 
    SIDEWAYS_ADX_THRESHOLD, 
    SIDEWAYS_MIN_BARS,
    CRISIS_VOLATILITY_THRESHOLD,
    CRISIS_SENTIMENT_THRESHOLD
)

class MarketAnalyzer:
    
    @staticmethod
    def analyze_trend(df: pd.DataFrame) -> Dict[str, any]:
        """Analyze market trend based on technical indicators"""
        try:
            if df.empty or len(df) < 50:
                return {'trend': 'neutral', 'strength': 0, 'direction': 'unknown'}
            
            last_candle = df.iloc[-1]
            
            # Determine trend direction
            if last_candle['sma_20'] > last_candle['sma_50']:
                direction = 'Alcista'
            elif last_candle['sma_20'] < last_candle['sma_50']:
                direction = 'Bajista'
            else:
                direction = 'Lateral'
            
            # Calculate trend strength based on ADX
            adx = last_candle.get('adx', 0)
            if adx >= 50:
                strength = 'Fuerte'
            elif adx >= 25:
                strength = 'Moderada'
            elif adx >= 10:
                strength = 'Débil'
            else:
                strength = 'Muy débil'
            
            return {
                'trend': direction.lower(),
                'strength': strength,
                'direction': direction,
                'adx': float(adx),
                'sma20': float(last_candle.get('sma_20', 0)),
                'sma50': float(last_candle.get('sma_50', 0))
            }
            
        except Exception as e:
            print(f"Error analyzing trend: {e}")
            return {'trend': 'neutral', 'strength': 0, 'direction': 'unknown'}
    
    @staticmethod
    def detect_sideways_market(df: pd.DataFrame) -> Dict[str, any]:
        """Detect if market is in sideways/ranging condition"""
        try:
            if len(df) < SIDEWAYS_MIN_BARS:
                return {'is_sideways': False, 'confidence': 0, 'reasons': ['Insufficient data']}
            
            recent_data = df.tail(SIDEWAYS_MIN_BARS)
            reasons = []
            
            # Check ADX for low trend strength
            avg_adx = recent_data['adx'].mean()
            if avg_adx < SIDEWAYS_ADX_THRESHOLD:
                reasons.append(f"ADX bajo ({avg_adx:.1f} < {SIDEWAYS_ADX_THRESHOLD})")
            
            # Check price range volatility
            price_range = (recent_data['high'].max() - recent_data['low'].min()) / recent_data['close'].mean()
            atr_ratio = recent_data['atr'].mean() / recent_data['close'].mean()
            
            if price_range < SIDEWAYS_ATR_THRESHOLD:
                reasons.append(f"Rango de precios estrecho ({price_range:.2%})")
            
            if atr_ratio < SIDEWAYS_ATR_THRESHOLD:
                reasons.append(f"Volatilidad baja (ATR ratio: {atr_ratio:.2%})")
            
            # Check for consolidation pattern
            sma20_std = recent_data['sma_20'].std()
            price_std = recent_data['close'].std()
            
            if sma20_std < price_std * 0.5:
                reasons.append("Consolidación en MA")
            
            # Determine if sideways
            is_sideways = len(reasons) >= 2
            confidence = min(len(reasons) / 3.0, 1.0)
            
            return {
                'is_sideways': is_sideways,
                'confidence': confidence,
                'reasons': reasons,
                'avg_adx': float(avg_adx),
                'price_range': float(price_range),
                'atr_ratio': float(atr_ratio)
            }
            
        except Exception as e:
            print(f"Error detecting sideways market: {e}")
            return {'is_sideways': False, 'confidence': 0, 'reasons': [str(e)]}
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """Calculate market volatility metrics"""
        try:
            if len(df) < period:
                return {'current_volatility': 0, 'avg_volatility': 0, 'volatility_ratio': 1}
            
            # Calculate rolling volatility
            returns = df['close'].pct_change()
            current_vol = returns.tail(period).std() * np.sqrt(252)  # Annualized
            avg_vol = returns.rolling(period).std().mean() * np.sqrt(252)
            
            volatility_ratio = current_vol / avg_vol if avg_vol > 0 else 1
            
            return {
                'current_volatility': float(current_vol),
                'avg_volatility': float(avg_vol),
                'volatility_ratio': float(volatility_ratio)
            }
            
        except Exception as e:
            print(f"Error calculating volatility: {e}")
            return {'current_volatility': 0, 'avg_volatility': 0, 'volatility_ratio': 1}
    
    @staticmethod
    def detect_crisis_conditions(df: pd.DataFrame, sentiment_score: float = 0) -> Dict[str, any]:
        """Detect crisis market conditions"""
        try:
            if df.empty:
                return {'is_crisis': False, 'confidence': 0, 'reasons': []}
            
            reasons = []
            confidence = 0
            
            # Check volatility spike
            volatility = MarketAnalyzer.calculate_volatility(df)
            if volatility['volatility_ratio'] > 2.0:
                reasons.append(f"Alta volatilidad ({volatility['current_volatility']:.2%})")
                confidence += 0.3
            
            # Check sentiment
            if sentiment_score < CRISIS_SENTIMENT_THRESHOLD:
                reasons.append(f"Sentimiento negativo ({sentiment_score:.2f})")
                confidence += 0.3
            
            # Check rapid price decline
            recent_returns = df['close'].pct_change().tail(5)
            if recent_returns.min() < -0.05:  # 5% decline in 5 periods
                reasons.append("Caída rápida de precios")
                confidence += 0.4
            
            # Check volume spike with price decline
            recent_volume = df['volume'].tail(5)
            volume_ma = df['volume'].tail(20).mean()
            if recent_volume.max() > volume_ma * 2 and recent_returns.min() < -0.03:
                reasons.append("Volumen alto con caída de precios")
                confidence += 0.3
            
            is_crisis = confidence > 0.5
            
            return {
                'is_crisis': is_crisis,
                'confidence': min(confidence, 1.0),
                'reasons': reasons,
                'volatility': volatility,
                'sentiment_score': sentiment_score
            }
            
        except Exception as e:
            print(f"Error detecting crisis: {e}")
            return {'is_crisis': False, 'confidence': 0, 'reasons': [str(e)]}
    
    @staticmethod
    def get_market_context(df: pd.DataFrame, sentiment_score: float = 0) -> Dict[str, any]:
        """Get comprehensive market context"""
        trend = MarketAnalyzer.analyze_trend(df)
        sideways = MarketAnalyzer.detect_sideways_market(df)
        volatility = MarketAnalyzer.calculate_volatility(df)
        crisis = MarketAnalyzer.detect_crisis_conditions(df, sentiment_score)
        
        # Determine trading recommendation
        blocked_reasons = []
        
        if sideways['is_sideways']:
            blocked_reasons.extend(sideways['reasons'])
        
        if crisis['is_crisis']:
            blocked_reasons.extend(crisis['reasons'])
        
        if trend['adx'] < 20:
            blocked_reasons.append("Tendencia débil")
        
        return {
            'trend': trend,
            'sideways': sideways,
            'volatility': volatility,
            'crisis': crisis,
            'market_status': 'normal' if not blocked_reasons else 'blocked',
            'blocked_reasons': blocked_reasons,
            'can_trade': len(blocked_reasons) == 0
        }