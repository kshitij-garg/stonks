"""
API Routes - Professional Trading Terminal
Complete API with watchlist, portfolio, patterns, and stock comparison
"""

from flask import Blueprint, jsonify, request
from services.stock_service import (
    get_nifty_stocks, 
    get_stock_data, 
    get_stock_info,
    get_market_indices,
    get_sector_performance,
    get_progress,
    PERIOD_MAP,
    get_cache_status,
    start_background_prefetch
)
from services.stock_universe import get_all_stocks, get_stocks_by_index, STOCK_COUNTS, get_sectors
from services.indicators import calculate_all_indicators, get_indicator_signals
from services.scoring import get_all_scored_stocks, screen_stocks, calculate_composite_score, get_recommendations
from services.patterns import detect_patterns, get_pattern_summary

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "cache": get_cache_status(), "stock_counts": STOCK_COUNTS})


@api_bp.route('/progress', methods=['GET'])
def get_loading_progress():
    return jsonify({"success": True, "data": get_progress()})


@api_bp.route('/cache-status', methods=['GET'])
def cache_status():
    try:
        from services.cache import get_all_cache_stats
        advanced_stats = get_all_cache_stats()
    except:
        advanced_stats = {}
    
    return jsonify({
        "success": True, 
        "data": get_cache_status(),
        "advanced": advanced_stats
    })


@api_bp.route('/prefetch', methods=['POST'])
def trigger_prefetch():
    try:
        start_background_prefetch()
        return jsonify({"success": True, "message": "Background prefetch started"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/search', methods=['GET'])
def search_stocks_api():
    """Quick search for stocks with autocomplete"""
    try:
        from services.stock_universe import search_stocks
        
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        results = search_stocks(query, limit)
        return jsonify({"success": True, "data": results, "query": query})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/universe', methods=['GET'])
def get_stock_universe():
    """Get all available stocks grouped by index"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "nifty50": get_stocks_by_index('nifty50'),
                "next50": get_stocks_by_index('next50'),
                "midcap50": get_stocks_by_index('midcap50'),
                "sectors": get_sectors(),
                "counts": STOCK_COUNTS
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/recommendations', methods=['GET'])
def get_stock_recommendations():
    try:
        timeframe = request.args.get('timeframe', 'weekly')
        index = request.args.get('index', 'all')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        recs = get_recommendations(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe
        )
        
        return jsonify({
            "success": True,
            "data": recs,
            "timeframe": timeframe,
            "cache_status": get_cache_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/top-performers', methods=['GET'])
def get_top_performers():
    try:
        timeframe = request.args.get('timeframe', 'weekly')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        all_stocks = get_all_scored_stocks(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe
        )
        
        return jsonify({
            "success": True,
            "data": {
                "top10": all_stocks[:10],
                "bottom10": list(reversed(all_stocks[-10:])),
                "total_analyzed": len(all_stocks),
                "timeframe": timeframe
            },
            "cache_status": get_cache_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/all-stocks', methods=['GET'])
def get_all_stocks_route():
    try:
        timeframe = request.args.get('timeframe', 'weekly')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        stocks = get_all_scored_stocks(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe
        )
        return jsonify({
            "success": True,
            "data": stocks,
            "total": len(stocks),
            "timeframe": timeframe,
            "cache_status": get_cache_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/stock/<symbol>', methods=['GET'])
def get_stock(symbol: str):
    try:
        symbol = symbol.upper()
        period = request.args.get('period', '6mo')
        
        df = get_stock_data(symbol, period=period)
        if df is None:
            return jsonify({"success": False, "error": f"Stock {symbol} not found"}), 404
        
        df = calculate_all_indicators(df)
        signals = get_indicator_signals(df)
        score_data = calculate_composite_score(symbol, df)
        patterns = detect_patterns(df)
        pattern_summary = get_pattern_summary(patterns)
        
        chart_data = [{
            "date": str(row['Date']),
            "open": round(float(row['Open']), 2),
            "high": round(float(row['High']), 2),
            "low": round(float(row['Low']), 2),
            "close": round(float(row['Close']), 2),
            "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
        } for _, row in df.iterrows()]
        
        return jsonify({
            "success": True,
            "data": {
                "scores": score_data.get('scores') if score_data else None,
                "signals": signals,
                "chartData": chart_data,
                "dcf": score_data.get('dcf') if score_data else None,
                "hurdle_rate": score_data.get('hurdle_rate') if score_data else None,
                "price_range": score_data.get('price_range') if score_data else None,
                "targets": score_data.get('targets') if score_data else None,
                "fundamentals": score_data.get('fundamentals') if score_data else None,
                "recommendation": score_data.get('recommendation') if score_data else None,
                "patterns": pattern_summary
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/compare', methods=['GET'])
def compare_stocks():
    """Compare multiple stocks side by side"""
    try:
        symbols = request.args.get('symbols', '').split(',')
        symbols = [s.strip().upper() for s in symbols if s.strip()]
        
        if not symbols:
            return jsonify({"success": False, "error": "No symbols provided"}), 400
        
        results = []
        for symbol in symbols[:5]:  # Max 5 stocks
            df = get_stock_data(symbol)
            if df is not None:
                df = calculate_all_indicators(df)
                score = calculate_composite_score(symbol, df)
                if score:
                    results.append(score)
        
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/market-overview', methods=['GET'])
def get_market_overview():
    try:
        indices = get_market_indices()
        return jsonify({"success": True, "data": indices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/sectors', methods=['GET'])
def get_sectors_route():
    try:
        sectors = get_sector_performance()
        return jsonify({"success": True, "data": sectors})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/screener', methods=['GET'])
def screener():
    try:
        timeframe = request.args.get('timeframe', 'weekly')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        filters = {
            'min_score': float(request.args.get('min_score', 0)),
            'min_rsi': float(request.args.get('min_rsi', 0)),
            'max_rsi': float(request.args.get('max_rsi', 100)),
            'sectors': None,
            'macd_signal': request.args.get('macd'),
            'valuation_status': request.args.get('valuation'),
            'min_upside': float(request.args.get('min_upside')) if request.args.get('min_upside') else None,
            'max_pe': float(request.args.get('max_pe')) if request.args.get('max_pe') else None
        }
        
        if request.args.get('sectors'):
            filters['sectors'] = [s.strip() for s in request.args.get('sectors').split(',') if s.strip()]
        
        stocks = screen_stocks(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe,
            **filters
        )
        
        return jsonify({
            "success": True,
            "data": stocks,
            "total": len(stocks),
            "timeframe": timeframe
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Watchlist Endpoints
@api_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    try:
        from services.watchlist import get_watchlist_stocks, get_watchlists
        
        watchlist_id = int(request.args.get('id', 1))
        stocks = get_watchlist_stocks(watchlist_id)
        lists = get_watchlists()
        
        return jsonify({"success": True, "data": {"stocks": stocks, "lists": lists}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    try:
        from services.watchlist import add_to_watchlist as add_stock
        
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        watchlist_id = data.get('watchlist_id', 1)
        price = data.get('price')
        
        if not symbol:
            return jsonify({"success": False, "error": "Symbol required"}), 400
        
        success = add_stock(symbol, watchlist_id, price)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    try:
        from services.watchlist import remove_from_watchlist as remove_stock
        
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        
        success = remove_stock(symbol)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Portfolio Endpoints
@api_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    try:
        from services.portfolio import get_portfolio_summary, get_holdings
        
        holdings = get_holdings()
        current_prices = {}
        
        for h in holdings:
            info = get_stock_info(h['symbol'])
            if info:
                current_prices[h['symbol']] = info.get('price', h['avg_price'])
        
        summary = get_portfolio_summary(current_prices)
        return jsonify({"success": True, "data": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/portfolio/add', methods=['POST'])
def add_to_portfolio():
    try:
        from services.portfolio import add_holding
        
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        quantity = float(data.get('quantity', 0))
        price = float(data.get('price', 0))
        
        if not symbol or quantity <= 0 or price <= 0:
            return jsonify({"success": False, "error": "Valid symbol, quantity and price required"}), 400
        
        success = add_holding(symbol, quantity, price)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/portfolio/remove', methods=['POST'])
def remove_from_portfolio():
    try:
        from services.portfolio import remove_holding
        
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        
        success = remove_holding(symbol)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/portfolio/import', methods=['POST'])
def import_portfolio():
    """Import holdings from CSV/Excel file (Zerodha, Groww, etc.)"""
    try:
        from services.csv_import import detect_broker_and_parse
        from services.portfolio import add_holding, get_holdings
        
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Read file content
        file_content = file.read()
        filename = file.filename.lower()
        
        # Parse the file
        holdings, errors, broker = detect_broker_and_parse(file_content, filename)
        
        if not holdings:
            return jsonify({
                "success": False, 
                "error": "No valid holdings found",
                "parse_errors": errors
            }), 400
        
        # Add holdings to portfolio
        added = 0
        import_errors = []
        
        for h in holdings:
            try:
                success = add_holding(
                    h['symbol'], 
                    h['quantity'], 
                    h['avg_price']
                )
                if success:
                    added += 1
            except Exception as e:
                import_errors.append(f"{h['symbol']}: {str(e)}")
        
        return jsonify({
            "success": True,
            "data": {
                "broker_detected": broker,
                "total_parsed": len(holdings),
                "added": added,
                "holdings": holdings
            },
            "parse_errors": errors,
            "import_errors": import_errors
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/portfolio/clear', methods=['POST'])
def clear_portfolio():
    """Clear all holdings from portfolio"""
    try:
        from services.portfolio import get_holdings, remove_holding
        
        holdings = get_holdings()
        for h in holdings:
            remove_holding(h['symbol'])
        
        return jsonify({"success": True, "removed": len(holdings)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/portfolio/analytics', methods=['GET'])
def get_portfolio_analytics_route():
    """Get comprehensive portfolio analytics with upside/downside predictions"""
    try:
        from services.portfolio import get_portfolio_analytics, get_holdings
        
        # Get all scored stocks with recommendations
        timeframe = request.args.get('timeframe', 'weekly')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        all_stocks = get_all_scored_stocks(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe
        )
        
        # Convert to dict keyed by symbol
        stock_data = {s['symbol']: s for s in all_stocks}
        
        analytics = get_portfolio_analytics(stock_data)
        return jsonify({"success": True, "data": analytics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Backtesting Endpoints
@api_bp.route('/backtest', methods=['GET'])
def get_backtest_results():
    try:
        from services.backtest import calculate_backtest_returns, get_tracking_stats
        
        days = int(request.args.get('days', 30))
        results = calculate_backtest_returns(days)
        stats = get_tracking_stats()
        
        return jsonify({"success": True, "data": results, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/backtest/save', methods=['POST'])
def save_snapshot():
    try:
        from services.backtest import save_recommendations, save_current_prices
        
        timeframe = request.args.get('timeframe', 'weekly')
        period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
        
        stocks = get_all_scored_stocks(
            period=period_config['period'],
            interval=period_config['interval'],
            timeframe=timeframe
        )
        
        save_recommendations(stocks, timeframe)
        save_current_prices(stocks)
        
        return jsonify({"success": True, "message": f"Saved {len(stocks)} recommendations"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/backtest/history', methods=['GET'])
def get_recommendation_history():
    """Get datewise recommendation history"""
    try:
        from services.backtest import get_recommendation_history
        
        days = int(request.args.get('days', 30))
        symbol = request.args.get('symbol', None)
        
        history = get_recommendation_history(days, symbol)
        
        # Group by date
        by_date = {}
        for rec in history:
            date = rec.get('timestamp', 'Unknown')
            if date not in by_date:
                by_date[date] = []
            by_date[date].append({
                'symbol': rec.get('symbol'),
                'action': rec.get('action'),
                'confidence': rec.get('confidence'),
                'price': rec.get('price_at_rec'),
                'dcf_value': rec.get('dcf_value'),
                'upside': rec.get('upside_target'),
                'score': rec.get('composite_score'),
                'sector': rec.get('sector')
            })
        
        # Convert to sorted list
        dates_list = []
        for date in sorted(by_date.keys(), reverse=True):
            dates_list.append({
                'date': date,
                'recommendations': by_date[date],
                'count': len(by_date[date]),
                'strong_buys': len([r for r in by_date[date] if r['action'] == 'STRONG BUY']),
                'buys': len([r for r in by_date[date] if r['action'] == 'BUY']),
                'sells': len([r for r in by_date[date] if r['action'] in ['SELL', 'STRONG SELL']])
            })
        
        return jsonify({
            "success": True, 
            "data": dates_list,
            "total_dates": len(dates_list)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Import pandas for type checking
import pandas as pd


# ===========================================
# COMMODITIES ENDPOINTS
# ===========================================

@api_bp.route('/commodities', methods=['GET'])
def get_commodities():
    """Get all commodity prices (Gold, Silver, Crude Oil)"""
    try:
        from services.commodities import get_all_commodities
        data = get_all_commodities()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/commodity/<symbol>', methods=['GET'])
def get_commodity(symbol: str):
    """Get single commodity with chart data"""
    try:
        from services.commodities import fetch_commodity_data
        period = request.args.get('period', '6mo')
        data = fetch_commodity_data(symbol.upper(), period)
        if not data:
            return jsonify({"success": False, "error": "Commodity not found"}), 404
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/market-summary', methods=['GET'])
def get_market_summary():
    """Get complete market summary (indices + commodities + currency)"""
    try:
        from services.commodities import get_market_summary
        data = get_market_summary()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===========================================
# ALERTS ENDPOINTS
# ===========================================

@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all active price alerts"""
    try:
        from services.alerts import get_active_alerts
        symbol = request.args.get('symbol')
        alerts = get_active_alerts(symbol)
        return jsonify({"success": True, "data": alerts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/alerts/create', methods=['POST'])
def create_alert():
    """Create a new price alert"""
    try:
        from services.alerts import create_alert as create_new_alert
        
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        target_price = float(data.get('target_price', 0))
        condition = data.get('condition', 'above')
        notes = data.get('notes', '')
        
        if not symbol or target_price <= 0:
            return jsonify({"success": False, "error": "Symbol and target_price required"}), 400
        
        alert_id = create_new_alert(symbol, target_price, condition, notes=notes)
        return jsonify({"success": True, "alert_id": alert_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/alerts/<int:alert_id>/delete', methods=['POST'])
def delete_alert_route(alert_id: int):
    """Delete an alert"""
    try:
        from services.alerts import delete_alert
        success = delete_alert(alert_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/alerts/check', methods=['POST'])
def check_alerts_route():
    """Check alerts against current prices"""
    try:
        from services.alerts import check_alerts, get_active_alerts
        
        # Get current prices for all symbols with alerts
        alerts = get_active_alerts()
        symbols = set(a['symbol'] for a in alerts)
        
        current_prices = {}
        for symbol in symbols:
            info = get_stock_info(symbol)
            if info:
                current_prices[symbol] = info.get('price', 0)
        
        triggered = check_alerts(current_prices)
        return jsonify({"success": True, "triggered": triggered})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/alerts/history', methods=['GET'])
def get_alert_history():
    """Get history of triggered alerts"""
    try:
        from services.alerts import get_alert_history
        limit = int(request.args.get('limit', 50))
        history = get_alert_history(limit)
        return jsonify({"success": True, "data": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===========================================
# FUNDAMENTALS ENDPOINTS
# ===========================================

@api_bp.route('/fundamentals/<symbol>', methods=['GET'])
def get_fundamentals(symbol: str):
    """Get comprehensive fundamental data"""
    try:
        from services.fundamentals import get_full_fundamentals
        data = get_full_fundamentals(symbol.upper())
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/fundamentals/<symbol>/quarterly', methods=['GET'])
def get_quarterly(symbol: str):
    """Get quarterly results"""
    try:
        from services.fundamentals import get_quarterly_results
        data = get_quarterly_results(symbol.upper())
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/fundamentals/<symbol>/balance-sheet', methods=['GET'])
def get_balance_sheet_route(symbol: str):
    """Get balance sheet"""
    try:
        from services.fundamentals import get_balance_sheet
        data = get_balance_sheet(symbol.upper())
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/fundamentals/<symbol>/peers', methods=['GET'])
def get_peers(symbol: str):
    """Get peer comparison"""
    try:
        from services.fundamentals import get_peer_comparison
        data = get_peer_comparison(symbol.upper())
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ===========================================
# CHART DATA ENDPOINTS
# ===========================================

@api_bp.route('/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol: str):
    """Get OHLC chart data for a stock"""
    try:
        period = request.args.get('period', '6mo')
        interval = request.args.get('interval', '1d')
        
        df = get_stock_data(symbol.upper(), period=period, interval=interval)
        if df is None:
            return jsonify({"success": False, "error": "No data"}), 404
        
        # Calculate indicators for overlays
        from services.indicators import calculate_all_indicators
        df = calculate_all_indicators(df)
        
        chart_data = []
        for _, row in df.iterrows():
            point = {
                "date": str(row.get('Date', '')),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']) if not pd.isna(row.get('Volume', 0)) else 0,
            }
            # Add indicators if available
            if 'SMA_20' in row:
                point['sma20'] = round(float(row['SMA_20']), 2) if not pd.isna(row['SMA_20']) else None
            if 'SMA_50' in row:
                point['sma50'] = round(float(row['SMA_50']), 2) if not pd.isna(row['SMA_50']) else None
            if 'EMA_12' in row:
                point['ema12'] = round(float(row['EMA_12']), 2) if not pd.isna(row['EMA_12']) else None
            if 'BB_Upper' in row:
                point['bb_upper'] = round(float(row['BB_Upper']), 2) if not pd.isna(row['BB_Upper']) else None
            if 'BB_Lower' in row:
                point['bb_lower'] = round(float(row['BB_Lower']), 2) if not pd.isna(row['BB_Lower']) else None
            if 'RSI' in row:
                point['rsi'] = round(float(row['RSI']), 2) if not pd.isna(row['RSI']) else None
            if 'MACD' in row:
                point['macd'] = round(float(row['MACD']), 4) if not pd.isna(row['MACD']) else None
            if 'MACD_Signal' in row:
                point['macd_signal'] = round(float(row['MACD_Signal']), 4) if not pd.isna(row['MACD_Signal']) else None
            
            chart_data.append(point)
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol.upper(),
                "period": period,
                "interval": interval,
                "candles": chart_data
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

