import pandas as pd
from typing import Dict, List
from datetime import datetime, date
from config import RISK_PER_TRADE, MAX_DAILY_TRADES
from models.trade import Trade

def calculate_position_size(entry_price: float, stop_loss: float, risk_amount: float) -> float:
    """Calculate position size based on risk management"""
    try:
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0
            
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit == 0:
            return 0.0
            
        position_size = risk_amount / risk_per_unit
        return max(0.0, position_size)
    except Exception as e:
        print(f"Error calculating position size: {e}")
        return 0.0

def validate_trade_conditions(df: pd.DataFrame, is_buy: bool) -> bool:
    """Validate trade conditions before execution"""
    try:
        if df.empty or len(df) < 50:
            return False
            
        last_candle = df.iloc[-1]
        
        # Check for valid technical indicators
        required_indicators = ['rsi', 'macd', 'adx', 'atr']
        for indicator in required_indicators:
            if indicator not in last_candle or pd.isna(last_candle[indicator]):
                return False
                
        # Check for extreme values
        if last_candle['rsi'] < 0 or last_candle['rsi'] > 100:
            return False
            
        if last_candle['adx'] < 0 or last_candle['adx'] > 100:
            return False
            
        if last_candle['atr'] <= 0:
            return False
            
        return True
    except Exception as e:
        print(f"Error validating trade conditions: {e}")
        return False

def can_trade_today(daily_trades: int, max_daily_trades: int = None) -> bool:
    """Check if trading is allowed today based on daily limit"""
    if max_daily_trades is None:
        max_daily_trades = MAX_DAILY_TRADES
    return daily_trades < max_daily_trades

def calculate_risk_metrics(entry_price: float, stop_loss: float, take_profit: float) -> Dict:
    """Calculate risk metrics for a trade"""
    try:
        risk_amount = abs(entry_price - stop_loss)
        reward_amount = abs(take_profit - entry_price)
        
        risk_percent = (risk_amount / entry_price) * 100
        reward_percent = (reward_amount / entry_price) * 100
        
        risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        return {
            'risk_amount': risk_amount,
            'reward_amount': reward_amount,
            'risk_percent': risk_percent,
            'reward_percent': reward_percent,
            'risk_reward_ratio': risk_reward_ratio,
            'distance_percent': risk_percent
        }
    except Exception as e:
        print(f"Error calculating risk metrics: {e}")
        return {
            'risk_amount': 0,
            'reward_amount': 0,
            'risk_percent': 0,
            'reward_percent': 0,
            'risk_reward_ratio': 0,
            'distance_percent': 0
        }

class RiskManager:
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.daily_trades = 0
        self.max_daily_trades = MAX_DAILY_TRADES
        self.risk_per_trade = RISK_PER_TRADE
        
    def update_balance(self, new_balance: float):
        """Update current balance"""
        self.current_balance = new_balance
        
    def increment_daily_trades(self):
        """Increment daily trade counter"""
        self.daily_trades += 1
        
    def reset_daily_trades(self):
        """Reset daily trade counter"""
        self.daily_trades = 0
        
    def can_trade(self) -> bool:
        """Check if trading is allowed"""
        return self.daily_trades < self.max_daily_trades
        
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on current balance"""
        risk_amount = self.current_balance * self.risk_per_trade
        return calculate_position_size(entry_price, stop_loss, risk_amount)
        
    def get_available_risk_amount(self) -> float:
        """Get available risk amount for next trade"""
        return self.current_balance * self.risk_per_trade