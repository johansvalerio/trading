import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from textblob import TextBlob
import numpy as np

class NewsAnalyzer:
    def __init__(self):
        self.news_api_key = None  # Puedes agregar tu API key de Alpha Vantage o NewsAPI
        self.sentiment_threshold = 0.3
        self.crisis_keywords = [
            'crash', 'crisis', 'panic', 'collapse', 'meltdown',
            'bankruptcy', 'default', 'recession', 'inflation', 'war',
            'sanctions', 'regulation', 'ban', 'hack', 'scandal',
            'volatility', 'plunge', 'plummet', 'tumble', 'sell-off'
        ]
        
    def get_crypto_news(self, symbol: str = 'BTC') -> List[Dict]:
        """Obtiene noticias relevantes de criptomonedas"""
        try:
            # Usar yfinance para obtener noticias de criptomonedas
            ticker = yf.Ticker(f"{symbol}-USD")
            news = ticker.news
            
            formatted_news = []
            for item in news[:10]:  # Limitar a las 10 noticias más recientes
                news_item = {
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                    'source': item.get('publisher', ''),
                    'url': item.get('link', ''),
                    'sentiment': self.analyze_sentiment(item.get('title', '') + ' ' + item.get('summary', ''))
                }
                formatted_news.append(news_item)
                
            return formatted_news
        except Exception as e:
            print(f"Error obteniendo noticias: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analiza el sentimiento de un texto"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Detectar crisis
            crisis_score = sum(1 for keyword in self.crisis_keywords 
                             if keyword.lower() in text.lower()) / len(self.crisis_keywords)
            
            return {
                'polarity': polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'is_crisis': crisis_score > 0.1,
                'crisis_intensity': crisis_score,
                'sentiment_label': 'positive' if polarity > self.sentiment_threshold else 
                                 'negative' if polarity < -self.sentiment_threshold else 'neutral'
            }
        except:
            return {'polarity': 0, 'subjectivity': 0, 'is_crisis': False, 'crisis_intensity': 0, 'sentiment_label': 'neutral'}
    

    
    def get_market_context(self, df: pd.DataFrame, symbol: str = 'BTC') -> Dict:
        """Obtiene el contexto de noticias y sentimiento del mercado"""
        news = self.get_crypto_news(symbol)
        
        # Analizar noticias recientes
        crisis_alerts = [n for n in news if n['sentiment']['is_crisis']]
        recent_sentiment = np.mean([n['sentiment']['polarity'] for n in news]) if news else 0
        
        return {
            'news': news[:5],  # Top 5 noticias
            'crisis_alerts': crisis_alerts,
            'overall_sentiment': 'positive' if recent_sentiment > 0.1 else 'negative' if recent_sentiment < -0.1 else 'neutral',
            'sentiment_score': float(recent_sentiment),
            'crisis_impact': sum(n['sentiment']['crisis_intensity'] for n in crisis_alerts)
        }