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
    return jsonify({"success": True, "data": get_cache_status()})


@api_bp.route('/prefetch', methods=['POST'])
def trigger_prefetch():
    try:
        start_background_prefetch()
        return jsonify({"success": True, "message": "Background prefetch started"})
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


# Import pandas for type checking
import pandas as pd
