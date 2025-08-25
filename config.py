# Configuration file for Forex Trading Bot

# Exchange Configuration
EXCHANGE = 'binance'
SYMBOL = 'BTCUSDT'
TIMEFRAME = '1h'

# Trading Configuration
INITIAL_BALANCE = 1000.0
RISK_PER_TRADE = 0.02  # 2% risk per trade
MAX_DAILY_TRADES = 3
MIN_RISK_REWARD = 1.5

# Technical Indicators Configuration
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
ADX_PERIOD = 14
ADX_THRESHOLD = 25
SMA_SHORT = 20
SMA_LONG = 50
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0

# Stop Loss Configuration
DYNAMIC_STOP_LOSS = True
STOP_LOSS_ATR_MULTIPLIER = 2.0

# Trend Configuration
TREND_CONFIRMATION = True
TREND_FILTER = True

# Moving Averages Configuration
MA_FAST = 20
MA_SLOW = 50

# API Configuration
API_BASE_URL = 'https://api.binance.com/api/v3'
UPDATE_INTERVAL = 60  # seconds

# News Configuration
NEWS_SOURCES = ['crypto_news', 'twitter', 'reddit']
SENTIMENT_THRESHOLD = 0.1

# Sideways Market Detection
SIDEWAYS_ATR_THRESHOLD = 0.5
SIDEWAYS_ADX_THRESHOLD = 20
SIDEWAYS_MIN_BARS = 20

# Crisis Detection
CRISIS_VOLATILITY_THRESHOLD = 0.1
CRISIS_SENTIMENT_THRESHOLD = -0.3