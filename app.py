import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Import new modules
from config import *
from models.trade import Trade
from services.indicators import TechnicalIndicators, add_technical_indicators, prepare_features
from services.risk_management import calculate_position_size, validate_trade_conditions, can_trade_today
from services.trading import TradingService
from services.market_analysis import MarketAnalyzer
from api.client import ExchangeClient, get_historical_data
from services.news_analyzer import NewsAnalyzer

app = Flask(__name__)

# Initialize services
news_analyzer = NewsAnalyzer()
trading_service = TradingService()
exchange_client = ExchangeClient()
market_analyzer = MarketAnalyzer()

# Global variables
daily_trades = 0
last_trade_day = None
current_balance = INITIAL_BALANCE

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Get trading data and analysis"""
    try:
        # Fetch historical data
        df = get_historical_data(SYMBOL, TIMEFRAME, 200)
        if df is None or df.empty:
            return jsonify({'error': 'No data available'}), 500
        
        # Add technical indicators
        df = add_technical_indicators(df)
        if df is None or df.empty:
            return jsonify({'error': 'Error processing indicators'}), 500
        
        # Get news sentiment analysis
        news_analysis = news_analyzer.get_market_context(df, SYMBOL)
        sentiment_score = news_analysis['sentiment_score']
        
        # Adjust sentiment based on crisis alerts
        if news_analysis['crisis_alerts']:
            sentiment_score -= 1.0
            
        # Get market context with sentiment
        market_context = market_analyzer.get_market_context(df, sentiment_score)
        
        # Prepare ML features
        features = prepare_features(df)
        if features is None or features.empty:
            return jsonify({'error': 'Error preparing features'}), 500
        
        # AI prediction
        ai_prediction = 0  # Default
        ai_prediction_data = None
        
        if len(features) >= 50:
            # Use recent features for prediction
            recent_features = features.tail(30)
            
            # Simple trend-based prediction for now
            last_candle = df.iloc[-1]
            
            # Determine prediction based on technical indicators
            is_golden_cross = last_candle['sma_20'] > last_candle['sma_50']
            is_death_cross = last_candle['sma_20'] < last_candle['sma_50']
            is_macd_bullish = last_candle['macd'] > last_candle['macd_signal']
            is_macd_bearish = last_candle['macd'] < last_candle['macd_signal']
            
            if is_golden_cross and is_macd_bullish and last_candle['rsi'] < 70:
                ai_prediction = 1
            elif is_death_cross and is_macd_bearish and last_candle['rsi'] > 30:
                ai_prediction = 0
            
            # Normalizar confianza a 0-100% basado en fuerza relativa del MACD
            macd_value = abs(last_candle['macd'])
            price = float(last_candle['close'])
            
            # Escalar MACD relativo al precio para obtener confianza significativa
            relative_strength = (macd_value / price) * 1000  # Multiplicador para escalar
            
            # Limitar entre 30-95% para evitar valores extremos
            normalized_confidence = min(max(relative_strength, 0.3), 0.95)
            
            ai_prediction_data = {
                'direction': 'ALCISTA' if ai_prediction == 1 else 'BAJISTA',
                'confidence': normalized_confidence,
                'change': last_candle['macd']
            }
        
        # Get current price
        current_price = float(df.iloc[-1]['close']) if not df.empty else 0.0
        
        # Check daily trades
        today = datetime.now().date()
        global daily_trades, last_trade_day, current_balance
        
        if last_trade_day != today:
            daily_trades = 0
            last_trade_day = today
        
        # Check open positions
        closed_trades, total_pnl = trading_service.check_open_positions(current_price, current_balance)
        
        # Generate signals based on market context
        buy_signal = {'active': False, 'price': 0, 'rsi': 0, 'macd': 0, 'id': 0, 'time_iso': ''}
        sell_signal = {'active': False, 'price': 0, 'rsi': 0, 'macd': 0, 'id': 0, 'time_iso': ''}
        stop_loss_info = {'active': False, 'entry_price': 0, 'stop_loss': 0, 'take_profit': 0, 'is_buy': False, 'distance_percent': 0}
        
        # Trading logic
        can_trade = market_context['can_trade'] and can_trade_today(daily_trades, MAX_DAILY_TRADES)
        skip_reasons = market_context['blocked_reasons'].copy()
        
        if not can_trade_today(daily_trades, MAX_DAILY_TRADES):
            skip_reasons.append("Límite diario de operaciones alcanzado")
        
        # Technical indicators
        last_candle = df.iloc[-1]
        current_rsi = last_candle['rsi']
        current_macd = last_candle['macd']
        current_macd_signal = last_candle['macd_signal']
        current_adx = last_candle['adx']
        current_atr = last_candle['atr']
        
        # Signal conditions
        is_golden_cross = last_candle['sma_20'] > last_candle['sma_50']
        is_death_cross = last_candle['sma_20'] < last_candle['sma_50']
        is_macd_bullish = current_macd > current_macd_signal
        is_macd_bearish = current_macd < current_macd_signal
        
        # Generate signals
        if can_trade:
            # Buy signal
            if is_golden_cross and is_macd_bullish and ai_prediction == 1:
                entry_price = current_price
                stop_loss = entry_price - (current_atr * ATR_MULTIPLIER)
                take_profit = entry_price + (current_atr * ATR_MULTIPLIER * MIN_RISK_REWARD)
                
                if validate_trade_conditions(df, is_buy=True):
                    trade = trading_service.execute_trade(
                        SYMBOL, True, entry_price, stop_loss, take_profit,
                        current_balance=current_balance
                    )
                    if trade:
                        buy_signal.update({
                            'active': True,
                            'price': round(float(entry_price), 4),
                            'rsi': round(float(current_rsi), 2),
                            'macd': round(float(current_macd), 6),
                            'id': int(datetime.now().timestamp() * 1000),
                            'time_iso': datetime.now().isoformat()
                        })
                        
                        stop_loss_info.update({
                            'active': True,
                            'entry_price': round(float(entry_price), 4),
                            'stop_loss': round(float(stop_loss), 4),
                            'take_profit': round(float(take_profit), 4),
                            'is_buy': True,
                            'distance_percent': round(abs((entry_price - stop_loss) / entry_price * 100), 2)
                        })
                        daily_trades += 1
            
            # Sell signal
            if is_death_cross and is_macd_bearish and ai_prediction == 0:
                entry_price = current_price
                stop_loss = entry_price + (current_atr * ATR_MULTIPLIER)
                take_profit = entry_price - (current_atr * ATR_MULTIPLIER * MIN_RISK_REWARD)
                
                if validate_trade_conditions(df, is_buy=False):
                    trade = trading_service.execute_trade(
                        SYMBOL, False, entry_price, stop_loss, take_profit,
                        current_balance=current_balance
                    )
                    if trade:
                        sell_signal.update({
                            'active': True,
                            'price': round(float(entry_price), 4),
                            'rsi': round(float(current_rsi), 2),
                            'macd': round(float(current_macd), 6),
                            'id': int(datetime.now().timestamp() * 1000),
                            'time_iso': datetime.now().isoformat()
                        })
                        
                        stop_loss_info.update({
                            'active': True,
                            'entry_price': round(float(entry_price), 4),
                            'stop_loss': round(float(stop_loss), 4),
                            'take_profit': round(float(take_profit), 4),
                            'is_buy': False,
                            'distance_percent': round(abs((entry_price - stop_loss) / entry_price * 100), 2)
                        })
                        daily_trades += 1
        
        # Prepare chart data
        x_axis = df.index.to_series().dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        
        # Create candlestick trace
        trace_candlestick = {
            'type': 'candlestick',
            'x': x_axis,
            'open': df['open'].fillna(0).astype(float).round(8).tolist(),
            'high': df['high'].fillna(0).astype(float).round(8).tolist(),
            'low': df['low'].fillna(0).astype(float).round(8).tolist(),
            'close': df['close'].fillna(0).astype(float).round(8).tolist(),
            'name': 'Precio',
            'yaxis': 'y2',
            'increasing': {'line': {'color': '#00C853'}},
            'decreasing': {'line': {'color': '#FF3D00'}}
        }
        
        # Add SL/TP lines if active
        data = [trace_candlestick]
        if stop_loss_info['active']:
            data.extend([
                {
                    'x': x_axis,
                    'y': [stop_loss_info['stop_loss']] * len(x_axis),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {'color': 'rgba(255, 0, 0, 0.7)', 'width': 2, 'dash': 'dash'},
                    'name': 'Stop Loss',
                    'yaxis': 'y2'
                },
                {
                    'x': x_axis,
                    'y': [stop_loss_info['take_profit']] * len(x_axis),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {'color': 'rgba(0, 200, 0, 0.7)', 'width': 2, 'dash': 'dash'},
                    'name': 'Take Profit',
                    'yaxis': 'y2'
                },
                {
                    'x': x_axis,
                    'y': [stop_loss_info['entry_price']] * len(x_axis),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {'color': 'rgba(255, 165, 0, 0.7)', 'width': 2, 'dash': 'solid'},
                    'name': 'Precio de Entrada',
                    'yaxis': 'y2'
                }
            ])
        
        # Determine signal text
        if buy_signal['active'] and sell_signal['active']:
            signal_text = "AMBAS SEÑALES"
        elif buy_signal['active']:
            signal_text = "COMPRA ACTIVA"
        elif sell_signal['active']:
            signal_text = "VENTA ACTIVA"
        else:
            signal_text = "SIN SEÑALES"
        
        # Calculate account metrics
        open_positions = trading_service.get_open_positions()
        total_pnl = trading_service.get_total_pnl()
        
        open_positions_info = []
        for pos_id, pos in open_positions.items():
            position_pnl = (current_price - pos.entry_price) * pos.size * (1 if pos.side == 'buy' else -1)
            position_pnl_percent = ((current_price / pos.entry_price) - 1) * 100 * (1 if pos.side == 'buy' else -1)
            
            open_positions_info.append({
                'symbol': pos.symbol,
                'side': pos.side,
                'entry_price': float(pos.entry_price),
                'current_price': float(current_price),
                'stop_loss': float(pos.stop_loss),
                'take_profit': float(pos.take_profit),
                'size': float(pos.size),
                'pnl': float(position_pnl),
                'pnl_percent': float(position_pnl_percent),
                'risk_amount': float(pos.risk_amount),
                'entry_time': pos.entry_time.isoformat(),
                'status': pos.status
            })
        
        # Calculate performance metrics
        trade_history = trading_service.get_trade_history()
        winning_trades = [t for t in trade_history if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trade_history if t.pnl and t.pnl <= 0]
        win_rate = (len(winning_trades) / len(trade_history) * 100) if trade_history else 0
        
        total_profit = sum(t.pnl for t in winning_trades if t.pnl) if winning_trades else 0
        total_loss = abs(sum(t.pnl for t in losing_trades if t.pnl)) if losing_trades else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
        
        # Calculate risk metrics
        current_risk = RISK_PER_TRADE * 100
        risk_reward_ratio = MIN_RISK_REWARD
        
        if last_candle is not None and 'atr' in last_candle and 'close' in last_candle:
            try:
                position_size = calculate_position_size(
                    current_price, 
                    current_price - (current_atr * ATR_MULTIPLIER),
                    current_balance * RISK_PER_TRADE
                )
            except Exception:
                position_size = 0.0
        else:
            position_size = 0.0
        
        # Prepare response
        response_data = {
            'indicators': {
                'adx': float(current_adx),
                'rsi': float(current_rsi),
                'macd': float(current_macd),
                'macd_signal': float(current_macd_signal),
                'sma_20': float(last_candle['sma_20']),
                'sma_50': float(last_candle['sma_50']),
                'atr': float(current_atr),
                'trend_strength': market_context['trend']['direction'],
                'ai_prediction': {
                    'prediction': 'ALCISTA' if ai_prediction == 1 else 'BAJISTA',
                    'confidence': ai_prediction_data['confidence'] if ai_prediction_data else 0,
                    'accuracy': trading_service.get_win_rate() / 100,
                    'success_rate': trading_service.get_win_rate() / 100
                },
                'risk_management': {
                    'risk_reward_ratio': float(risk_reward_ratio),
                    'position_size': float(position_size),
                    'trade_risk': float(current_risk)
                },
                'volume_analysis': {
                    'ratio': float(last_candle.get('volume_ratio', 1.0)),
                    'alert': False,
                    'current_volume': float(last_candle.get('volume', 0)),
                    'average_volume': float(last_candle.get('volume_ma', 0))
                },
                'adx': float(current_adx),
                'rsi': float(current_rsi),
                'macd': float(current_macd),
                'macd_signal': float(current_macd_signal),
                'sma_20': float(last_candle['sma_20']),
                'sma_50': float(last_candle['sma_50']),
                'atr': float(current_atr),
                'trend_strength': market_context['trend']['direction'],
                'balance': float(current_balance),
                'daily_trades': daily_trades,
                'max_daily_trades': MAX_DAILY_TRADES
            },
            'market_context': market_context,
            'news_analysis': {
                'overall_sentiment': news_analysis['overall_sentiment'],
                'crisis_alerts': len(news_analysis['crisis_alerts']),
                'sentiment_score': news_analysis['sentiment_score'],
                'crisis_impact': news_analysis['crisis_impact'],
                'recent_news': news_analysis['news'][:3] if news_analysis['news'] else []
            },
            'graph': {
                'data': data,
                'layout': {
                    'template': 'plotly_dark',
                    'title': {
                        'text': f"{SYMBOL} - Análisis en Tiempo Real<br><sub>Señal actual: {signal_text}</sub>",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'color': '#e0e0e0'}
                    },
                    'font': {'size': 16, 'color': '#e0e0e0', 'family': 'Arial'},
                    'plot_bgcolor': '#121212',
                    'paper_bgcolor': '#1e1e1e',
                    'xaxis': {
                        'title': {'text': '<b>Fecha</b>', 'font': {'color': '#e0e0e0'}},
                        'rangeslider': {
                            'visible': True,
                            'thickness': 0.1,
                            'bgcolor': 'rgba(0,0,0,0.3)',
                            'bordercolor': 'rgba(255, 255, 255, 0.1)'
                        },
                        'type': 'date',
                        'gridcolor': 'rgba(255, 255, 255, 0.1)',
                        'showline': True,
                        'linecolor': 'rgba(255, 255, 255, 0.3)',
                        'mirror': True,
                        'tickfont': {'color': '#a0a0a0'},
                        'zerolinecolor': 'rgba(255, 255, 255, 0.1)'
                    },
                    'yaxis': {
                        'title': {'text': '<b>Precio (USDT)</b>', 'font': {'color': '#e0a0a0'}},
                        'gridcolor': 'rgba(255, 255, 255, 0.08)',
                        'showline': True,
                        'linecolor': 'rgba(255, 255, 255, 0.2)',
                        'mirror': True,
                        'tickfont': {'color': '#a0a0a0'}
                    },
                    'showlegend': True,
                    'legend': {
                        'orientation': 'h',
                        'yanchor': 'bottom',
                        'y': 1.02,
                        'xanchor': 'right',
                        'x': 1,
                        'bgcolor': 'rgba(0,0,0,0.7)',
                        'font': {'color': 'white'}
                    },
                    'template': 'plotly_dark',
                    'plot_bgcolor': 'rgba(0,0,0,0.3)',
                    'paper_bgcolor': 'rgba(0,0,0,0.5)',
                    'height': 700,
                    'margin': {'l': 60, 'r': 30, 't': 100, 'b': 60},
                    'hovermode': 'x unified',
                    'hoverlabel': {
                        'bgcolor': 'rgba(0,0,0,0.9)',
                        'font_size': 12,
                        'font_color': 'white'
                    }
                }
            },
            'signal': signal_text,
            'buy_signal': buy_signal,
            'sell_signal': sell_signal,
            'last_price': float(current_price),
            'rsi': float(current_rsi),
            'macd': float(current_macd),
            'macd_signal': float(current_macd_signal),
            'sma_20': float(last_candle['sma_20']),
            'sma_50': float(last_candle['sma_50']),
            'bb_upper': float(last_candle.get('bb_upper', 0)),
            'bb_lower': float(last_candle.get('bb_lower', 0)),
            'adx': float(current_adx),
            'atr': float(current_atr),
            'ai_prediction': int(ai_prediction),
            'trend_status': market_context['trend']['direction'],
            'account_info': {
                'balance': float(current_balance),
                'equity': float(current_balance + total_pnl),
                'used_margin': sum(float(pos['size'] * pos['entry_price'] * 0.1) for pos in open_positions_info),
                'free_margin': float((current_balance + total_pnl) - sum(pos['size'] * pos['entry_price'] * 0.1 for pos in open_positions_info)),
                'margin_level': float(((current_balance + total_pnl) / sum(pos['size'] * pos['entry_price'] * 0.1 for pos in open_positions_info) * 100)) if open_positions_info else 0.0,
                'daily_trades': daily_trades,
                'max_daily_trades': MAX_DAILY_TRADES,
                'total_pnl': float(total_pnl),
                'win_rate': float(trading_service.get_win_rate())
            },
            'trading_info': {
                'open_positions': open_positions_info,
                'recent_trades': [{
                    'id': t.id,
                    'symbol': t.symbol,
                    'side': t.side,
                    'entry_price': float(t.entry_price),
                    'exit_price': float(t.exit_price) if t.exit_price else None,
                    'size': float(t.size),
                    'pnl': float(t.pnl) if t.pnl else 0.0,
                    'pnl_percent': float(t.pnl_percent) if t.pnl_percent else 0.0,
                    'entry_time': t.entry_time.isoformat(),
                    'exit_time': t.exit_time.isoformat() if t.exit_time else None,
                    'status': t.status,
                    'duration': (t.exit_time - t.entry_time).total_seconds() / 60 if t.exit_time else None
                } for t in trading_service.get_trade_history()[-5:]]
            }
        }
        
        response_data['stop_loss_info'] = stop_loss_info
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print("Error in get_data:")
        print(str(e))
        print(traceback.format_exc())
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}',
            'graph': {'data': [], 'layout': {}},
            'buy_signal': {'active': False, 'price': 0, 'rsi': 0, 'macd': 0, 'id': 0, 'time_iso': ''},
            'sell_signal': {'active': False, 'price': 0, 'rsi': 0, 'macd': 0, 'id': 0, 'time_iso': ''},
            'stop_loss_info': {'active': False, 'entry_price': 0, 'stop_loss': 0, 'take_profit': 0, 'is_buy': False, 'distance_percent': 0},
            'last_price': 0,
            'rsi': 0,
            'macd': 0,
            'macd_signal': 0,
            'sma_20': 0,
            'sma_50': 0,
            'bb_upper': 0,
            'bb_lower': 0
        }), 500

@app.route('/api/reset')
def reset_trading():
    """Reset trading state for testing"""
    global daily_trades, current_balance
    daily_trades = 0
    current_balance = INITIAL_BALANCE
    trading_service = TradingService()  # Reset trading service
    return jsonify({'success': True, 'message': 'Trading reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)
