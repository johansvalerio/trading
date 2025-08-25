# 🤖 AI Forex Trading Bot

An advanced automated trading system for cryptocurrency markets with AI-powered signals, comprehensive risk management, and real-time market analysis.

## 🚀 Features

### Core Trading Engine
- **Real-time market analysis** with 1-hour timeframe monitoring
- **AI-powered trading signals** using Random Forest algorithms
- **Advanced technical indicators** (RSI, MACD, ADX, ATR, Bollinger Bands)
- **Trend detection** with moving averages and momentum analysis

### Risk Management
- **Position sizing** based on ATR (Average True Range)
- **Dynamic stop-loss** and take-profit levels
- **Maximum daily trades** limit (configurable)
- **Risk per trade** management (1% default)
- **Risk-reward ratio** optimization (minimum 2:1)

### Market Intelligence
- **News sentiment analysis** for market context
- **Volatility detection** and crisis alerts
- **Sideways market detection** to avoid false signals
- **Volume analysis** with anomaly detection

### Portfolio Management
- **Real-time P&L tracking**
- **Win rate calculation**
- **Performance metrics** dashboard
- **Trade history** with detailed analytics
- **Open positions** monitoring

## 🏗️ Refactored Architecture

### Modular Design
The codebase has been completely refactored into a clean, modular structure:

```
forex_trading_bot/
├── app.py                 # Main Flask application (refactored)
├── config.py             # Centralized configuration
├── models/
│   ├── __init__.py
│   └── trade.py          # Trade data model
├── services/
│   ├── __init__.py
│   ├── indicators.py     # Technical indicators service
│   ├── risk_management.py # Risk management service
│   ├── trading.py        # Trading execution service
│   └── market_analysis.py # Market context service
├── api/
│   ├── __init__.py
│   └── client.py         # Exchange API client
├── utils/
│   ├── __init__.py
│   └── helpers.py        # Utility functions
├── templates/
│   └── index.html        # Web interface
├── news_analyzer.py      # News sentiment analysis
└── requirements.txt      # Dependencies
```

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🛠️ Installation

1. Clone this repository or download the files
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## 🎯 Usage

1. Start the application:
   ```
   python app.py
   ```
2. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```
3. Configure the currency pair and timeframe according to your preferences
4. Watch the AI-generated trading signals

## ⚙️ Configuration

You can modify the following parameters in the `config.py` file:

- `SYMBOL`: Default currency pair (e.g., 'BTC/USDT')
- `TIMEFRAME`: Data timeframe (e.g., '1h' for 1 hour)
- `RISK_PER_TRADE`: Risk percentage per trade (default: 1%)
- `MAX_DAILY_TRADES`: Maximum trades per day (default: 5)

## ⚠️ Warning

This software is for educational and research purposes only. We do not guarantee profits and are not responsible for any financial losses. Cryptocurrency trading involves significant risks.

## 📄 License

This project is under the MIT License.
