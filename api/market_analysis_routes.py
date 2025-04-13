from flask import jsonify, request
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register market analysis routes with the Flask application"""
    
    @app.route('/api/market-analysis/get-data', methods=['POST'])
    def api_get_market_analysis():
        """Get market analysis data based on the requested timeframe"""
        data = request.json
        timeframe = data.get('timeframe', '1d')
        
        try:
            # Generate mock market data
            mock_data = generate_mock_market_data(timeframe)
            
            return jsonify({
                'success': True,
                'data': mock_data
            })
        except Exception as e:
            logger.error(f"Error in market analysis data: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/ai-insights/market-analysis', methods=['POST'])
    def api_get_ai_insights():
        """Get AI-powered insights for market analysis"""
        data = request.json
        timeframe = data.get('timeframe', '1d')
        
        try:
            # Generate AI insights based on available data
            insights = generate_ai_market_insights(timeframe)
            
            return jsonify({
                'success': True,
                'market_summary': insights['market_summary'],
                'trade_suggestions': insights['trade_suggestions'],
                'market_trends': insights['market_trends']
            })
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger.info("Successfully registered market analysis routes")
    return True

def generate_mock_market_data(timeframe):
    """Generate mock market data for the given timeframe"""
    # Generate mock market indices data
    mock_indices = [
        { 
            'name': 'S&P 500', 
            'symbol': 'SPX', 
            'price': 5250.43, 
            'change': random.random() * 2 - 0.5, 
            'volume': 2543000000 
        },
        { 
            'name': 'Dow Jones', 
            'symbol': 'DJI', 
            'price': 38765.42, 
            'change': random.random() * 2 - 0.5, 
            'volume': 342000000 
        },
        { 
            'name': 'Nasdaq', 
            'symbol': 'COMP', 
            'price': 16432.78, 
            'change': random.random() * 2 - 0.5, 
            'volume': 5230000000 
        },
        { 
            'name': 'Russell 2000', 
            'symbol': 'RUT', 
            'price': 2152.32, 
            'change': random.random() * 2 - 0.5, 
            'volume': 1250000000 
        },
        { 
            'name': 'VIX', 
            'symbol': 'VIX', 
            'price': 16.25, 
            'change': random.random() * 5 - 2.5, 
            'volume': None 
        }
    ]

    # Generate mock sector performance data
    mock_sectors = [
        { 'name': 'Technology', 'change': random.random() * 4 - 1.5, 'volume': 3240000000 },
        { 'name': 'Healthcare', 'change': random.random() * 4 - 1.5, 'volume': 1820000000 },
        { 'name': 'Financials', 'change': random.random() * 4 - 1.5, 'volume': 2150000000 },
        { 'name': 'Consumer Discretionary', 'change': random.random() * 4 - 1.5, 'volume': 1970000000 },
        { 'name': 'Communication Services', 'change': random.random() * 4 - 1.5, 'volume': 1650000000 },
        { 'name': 'Industrials', 'change': random.random() * 4 - 1.5, 'volume': 1430000000 },
        { 'name': 'Consumer Staples', 'change': random.random() * 3 - 1, 'volume': 1280000000 },
        { 'name': 'Energy', 'change': random.random() * 5 - 2, 'volume': 1920000000 },
        { 'name': 'Utilities', 'change': random.random() * 2 - 0.5, 'volume': 980000000 },
        { 'name': 'Real Estate', 'change': random.random() * 3 - 1, 'volume': 1120000000 },
        { 'name': 'Materials', 'change': random.random() * 3 - 1, 'volume': 1050000000 }
    ]

    # Generate mock market breadth data
    mock_breadth = {
        'advance_decline_ratio': round(random.random() * 2 + 0.5, 2),
        'advancing_stocks': int(random.random() * 2000 + 1000),
        'declining_stocks': int(random.random() * 1500 + 500),
        'new_highs': int(random.random() * 300 + 50),
        'new_lows': int(random.random() * 100 + 10),
        'stocks_above_200d_ma': f"{int(random.random() * 30 + 50)}%",
        'stocks_above_50d_ma': f"{int(random.random() * 30 + 40)}%",
        'mcclellan_oscillator': round(random.random() * 200 - 100, 2),
        'cumulative_volume': f"{'+' if random.random() > 0.5 else '-'}{round(random.random() * 2, 2)}B"
    }

    # Generate mock fear & greed data
    mock_fear_greed_value = int(random.random() * 100)
    mock_fear_greed_rating = ""
    
    # Determine the fear/greed rating based on the value
    if mock_fear_greed_value <= 25:
        mock_fear_greed_rating = 'Extreme Fear'
    elif mock_fear_greed_value <= 45:
        mock_fear_greed_rating = 'Fear'
    elif mock_fear_greed_value <= 55:
        mock_fear_greed_rating = 'Neutral'
    elif mock_fear_greed_value <= 75:
        mock_fear_greed_rating = 'Greed'
    else:
        mock_fear_greed_rating = 'Extreme Greed'
    
    mock_fear_greed = {
        'value': mock_fear_greed_value,
        'rating': mock_fear_greed_rating,
        'components': {
            'stock_price_strength': int(random.random() * 100),
            'stock_price_breadth': int(random.random() * 100),
            'put_call_ratio': int(random.random() * 100),
            'market_volatility': int(random.random() * 100),
            'safe_haven_demand': int(random.random() * 100),
            'junk_bond_demand': int(random.random() * 100)
        }
    }

    # Generate mock economic indicators
    mock_economic_indicators = [
        {
            'name': 'Unemployment Rate',
            'value': f"{round(random.random() * 2 + 3, 1)}%",
            'previous': f"{round(random.random() * 2 + 3, 1)}%",
            'impact': 'positive' if random.random() > 0.5 else 'negative'
        },
        {
            'name': 'GDP Growth Rate',
            'value': f"{round(random.random() * 3 + 1, 1)}%",
            'previous': f"{round(random.random() * 3 + 1, 1)}%",
            'impact': 'positive' if random.random() > 0.5 else 'negative'
        },
        {
            'name': 'Inflation Rate',
            'value': f"{round(random.random() * 4 + 1, 1)}%",
            'previous': f"{round(random.random() * 4 + 1, 1)}%",
            'impact': 'positive' if random.random() > 0.6 else 'negative'
        },
        {
            'name': 'Interest Rate',
            'value': f"{round(random.random() * 3 + 3, 2)}%",
            'previous': f"{round(random.random() * 3 + 3, 2)}%",
            'impact': 'positive' if random.random() > 0.4 else 'negative'
        },
        {
            'name': 'Consumer Sentiment',
            'value': int(random.random() * 30 + 70),
            'previous': int(random.random() * 30 + 70),
            'impact': 'positive' if random.random() > 0.5 else 'negative'
        },
        {
            'name': 'Retail Sales',
            'value': f"{round(random.random() * 2 - 0.5, 1)}%",
            'previous': f"{round(random.random() * 2 - 0.5, 1)}%",
            'impact': 'positive' if random.random() > 0.5 else 'negative'
        }
    ]

    return {
        'indices': mock_indices,
        'sectors': mock_sectors,
        'breadth': mock_breadth,
        'fear_greed': mock_fear_greed,
        'economic_indicators': mock_economic_indicators
    }

def generate_ai_market_insights(timeframe):
    """Generate AI-powered market insights based on current market conditions"""
    # In a real implementation, this would use actual market data and GPT or another AI model
    # to generate meaningful insights about the market
    
    # For now, we'll create intelligent mock data
    market_sentiment = 'bullish' if random.random() > 0.5 else 'bearish'
    market_volatility = 'high' if random.random() > 0.7 else 'moderate'
    
    # Base factors that drive our mock analysis
    tech_sentiment = random.random() > 0.6  # True = positive, False = negative
    fed_policy = random.random() > 0.5  # True = hawkish, False = dovish
    inflation_trend = random.random() > 0.5  # True = rising, False = falling
    
    sectors_strength = {
        'Technology': 0.8 if tech_sentiment else 0.4,
        'Financials': 0.7 if fed_policy else 0.5,
        'Consumer Discretionary': 0.6 if not inflation_trend else 0.3,
        'Energy': 0.5 if inflation_trend else 0.7,
        'Healthcare': 0.6,  # More stable sector
        'Communication Services': 0.7 if tech_sentiment else 0.5,
        'Industrials': 0.5,
        'Utilities': 0.4 if fed_policy else 0.7,
        'Real Estate': 0.3 if fed_policy else 0.6,
        'Materials': 0.5 if inflation_trend else 0.6
    }
    
    # Generate a coherent market summary based on our factors
    bullish_indices = "trending upward, making new highs"
    bearish_indices = "experiencing downward pressure with key support levels being tested"
    tech_positive = "The technology sector is leading the market higher, with strong momentum in AI and semiconductor stocks."
    tech_negative = "Technology stocks are underperforming, with concerns about valuation and growth prospects."
    fed_hawkish = "The Federal Reserve's hawkish stance on interest rates is supporting financial stocks but pressuring rate-sensitive sectors."
    fed_dovish = "The Federal Reserve's dovish signals are boosting real estate and utilities sectors, while financials lag."
    inflation_rising = "Inflation data came in hotter than expected, which is contributing to market uncertainty."
    inflation_falling = "Inflation appears to be cooling, providing optimism for consumer stocks."
    trend_continue = "continuation of the current trend"
    trend_reverse = "reversal in the near future"
    volume_strong = "strong"
    volume_weak = "weak"
    
    market_summary = f"""The market is currently showing {market_sentiment} sentiment with {market_volatility} volatility. 
    Major indices are {bullish_indices if market_sentiment == 'bullish' else bearish_indices} amid recent economic data.
    {tech_positive if tech_sentiment else tech_negative} 
    {fed_hawkish if fed_policy else fed_dovish}
    {inflation_rising if inflation_trend else inflation_falling}
    Technical indicators suggest a potential {trend_continue if random.random() > 0.5 else trend_reverse}. 
    Volume analysis indicates {volume_strong if random.random() > 0.5 else volume_weak} institutional participation."""
    
    # Generate trade suggestions based on our market scenario
    top_sectors = sorted(sectors_strength.items(), key=lambda x: x[1], reverse=True)[:3]
    bottom_sectors = sorted(sectors_strength.items(), key=lambda x: x[1])[:2]
    
    # Map sectors to representative stocks
    sector_to_stocks = {
        'Technology': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'CRM'],
        'Financials': ['JPM', 'BAC', 'GS', 'MS', 'V'],
        'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'NKE', 'SBUX'],
        'Energy': ['XOM', 'CVX', 'COP', 'PSX', 'EOG'],
        'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABT', 'MRK'],
        'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA'],
        'Industrials': ['HON', 'UNP', 'CAT', 'DE', 'GE'],
        'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP'],
        'Real Estate': ['AMT', 'PLD', 'CCI', 'SPG', 'EQIX'],
        'Materials': ['LIN', 'APD', 'ECL', 'NEM', 'FCX']
    }
    
    # Generate trade suggestions favoring top sectors (BUY) and fading bottom sectors (SELL)
    trade_suggestions = []
    
    # Add BUY recommendations from strong sectors
    for sector, strength in top_sectors:
        stock = random.choice(sector_to_stocks[sector])
        base_price = 100 + random.random() * 900  # Random base price between $100-$1000
        
        trade_suggestions.append({
            'symbol': stock,
            'action': 'BUY',
            'confidence': int(strength * 100),
            'reason': f"Strong {sector} sector momentum and favorable technical setup",
            'target_price': round(base_price * (1 + random.random() * 0.15), 2),  # 0-15% upside
            'stop_loss': round(base_price * (1 - random.random() * 0.07), 2)  # 0-7% downside protection
        })
    
    # Add SELL recommendations from weak sectors
    for sector, strength in bottom_sectors:
        stock = random.choice(sector_to_stocks[sector])
        base_price = 100 + random.random() * 900
        
        trade_suggestions.append({
            'symbol': stock,
            'action': 'SELL',
            'confidence': int((1-strength) * 100),
            'reason': f"Weak {sector} sector performance and deteriorating technical indicators",
            'target_price': round(base_price * (1 - random.random() * 0.12), 2),  # 0-12% downside target
            'stop_loss': round(base_price * (1 + random.random() * 0.05), 2)  # 0-5% upside risk
        })
    
    # Generate market trends based on our scenario
    market_trends = []
    
    # Technology-related trend
    tech_trend_name = 'AI and Semiconductor Growth' if tech_sentiment else 'Tech Sector Rotation'
    tech_trend_strength = int((0.7 + random.random() * 0.3) * 100) if tech_sentiment else int((0.4 + random.random() * 0.3) * 100)
    tech_trend_duration = 'Long-term' if tech_sentiment else 'Medium-term'
    tech_trend_sectors = ['Technology', 'Communication Services', 'Consumer Discretionary']
    tech_trend_analysis = 'Continued strong demand for AI chips and infrastructure' if tech_sentiment else 'Rotation from high-growth tech to value-oriented technology subsectors'
    
    market_trends.append({
        'trend': tech_trend_name,
        'strength': tech_trend_strength,
        'duration': tech_trend_duration,
        'affected_sectors': tech_trend_sectors,
        'analysis': tech_trend_analysis
    })
    
    # Federal Reserve policy trend
    fed_trend_name = 'Federal Reserve Tightening Cycle' if fed_policy else 'Interest Rate Stabilization'
    fed_trend_strength = int((0.6 + random.random() * 0.3) * 100)
    fed_trend_duration = 'Medium-term'
    fed_trend_sectors = ['Financials', 'Real Estate', 'Utilities']
    fed_trend_analysis = 'Continued rate hikes affecting debt-heavy sectors' if fed_policy else 'Potential pause in rate hikes supporting interest rate sensitive sectors'
    
    market_trends.append({
        'trend': fed_trend_name,
        'strength': fed_trend_strength,
        'duration': fed_trend_duration,
        'affected_sectors': fed_trend_sectors,
        'analysis': fed_trend_analysis
    })
    
    # Inflation or economic trend
    inflation_trend_name = 'Inflationary Pressure' if inflation_trend else 'Consumer Spending Resilience'
    inflation_trend_strength = int((0.5 + random.random() * 0.4) * 100)
    inflation_trend_duration = 'Medium-term'
    inflation_trend_sectors = ['Energy', 'Materials', 'Consumer Staples'] if inflation_trend else ['Consumer Discretionary', 'Communication Services', 'Financials']
    inflation_trend_analysis = 'Persistent inflation affecting profit margins across multiple sectors' if inflation_trend else 'Strong consumer balance sheets supporting discretionary spending despite economic concerns'
    
    market_trends.append({
        'trend': inflation_trend_name,
        'strength': inflation_trend_strength,
        'duration': inflation_trend_duration,
        'affected_sectors': inflation_trend_sectors,
        'analysis': inflation_trend_analysis
    })
    
    return {
        'market_summary': market_summary,
        'trade_suggestions': trade_suggestions,
        'market_trends': market_trends
    } 