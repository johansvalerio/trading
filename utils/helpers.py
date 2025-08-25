import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any

def can_trade_today(daily_trades: int, max_daily_trades: int) -> bool:
    """Check if trading is allowed today based on daily limit"""
    return daily_trades < max_daily_trades

def format_currency(value: float, currency: str = 'USD') -> str:
    """Format currency value with appropriate decimal places"""
    if currency.upper() == 'USD':
        return f"${value:.2f}"
    elif currency.upper() == 'BTC':
        return f"{value:.8f} BTC"
    else:
        return f"{value:.4f} {currency}"

def format_percentage(value: float) -> str:
    """Format percentage value"""
    return f"{value:.2f}%"

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def calculate_time_difference(start_time: datetime, end_time: datetime) -> str:
    """Calculate and format time difference"""
    diff = end_time - start_time
    hours = diff.total_seconds() / 3600
    minutes = (diff.total_seconds() % 3600) / 60
    
    if hours >= 1:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate if dataframe has required columns"""
    if df is None or df.empty:
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0

def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Get summary statistics for a dataframe"""
    if df is None or df.empty:
        return {}
    
    return {
        'rows': len(df),
        'columns': list(df.columns),
        'start_date': df.index.min().strftime('%Y-%m-%d') if hasattr(df.index, 'strftime') else str(df.index.min()),
        'end_date': df.index.max().strftime('%Y-%m-%d') if hasattr(df.index, 'strftime') else str(df.index.max()),
        'price_range': {
            'min': float(df['low'].min()) if 'low' in df.columns else None,
            'max': float(df['high'].max()) if 'high' in df.columns else None,
            'avg': float(df['close'].mean()) if 'close' in df.columns else None
        }
    }

def safe_get_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_get_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def create_progress_bar(current: float, maximum: float, length: int = 20) -> str:
    """Create a text-based progress bar"""
    if maximum <= 0:
        return "[----------]"
    
    percentage = min(max(current / maximum, 0), 1)
    filled = int(length * percentage)
    bar = "█" * filled + "░" * (length - filled)
    
    return f"[{bar}] {percentage:.1%}"

def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_market_hours_status() -> Dict[str, str]:
    """Get current market hours status (for crypto, always open)"""
    now = datetime.now()
    return {
        'status': 'Open',
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': 'UTC',
        'market_type': 'Crypto (24/7)'
    }

def calculate_risk_reward(entry: float, stop: float, target: float, is_long: bool = True) -> Dict[str, float]:
    """Calculate risk/reward metrics"""
    try:
        risk = abs(entry - stop)
        reward = abs(target - entry)
        
        if risk == 0:
            return {'risk': 0, 'reward': 0, 'ratio': 0}
        
        ratio = reward / risk
        risk_percent = (risk / entry) * 100
        reward_percent = (reward / entry) * 100
        
        return {
            'risk': risk,
            'reward': reward,
            'ratio': ratio,
            'risk_percent': risk_percent,
            'reward_percent': reward_percent
        }
    except Exception:
        return {'risk': 0, 'reward': 0, 'ratio': 0, 'risk_percent': 0, 'reward_percent': 0}