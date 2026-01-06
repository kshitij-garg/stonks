"""
India Stock Market Analyzer - Flask Backend
Main application entry point
"""

from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
import os
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://kshitij-garg.github.io"])

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health():
    return {"status": "healthy", "message": "Stonks by KG API", "timestamp": datetime.now().isoformat()}


def save_daily_recommendations():
    """Background task to save today's recommendations for backtesting"""
    try:
        from services.scoring import get_all_scored_stocks
        from services.backtest import save_recommendations, save_current_prices
        
        print("[Backtest] Saving daily recommendations...")
        stocks = get_all_scored_stocks(timeframe='weekly')
        
        if stocks:
            save_recommendations(stocks, 'weekly')
            save_current_prices(stocks)
            print(f"[Backtest] Saved {len(stocks)} recommendations for {datetime.now().strftime('%Y-%m-%d')}")
        else:
            print("[Backtest] No stocks to save")
    except Exception as e:
        print(f"[Backtest] Error saving recommendations: {e}")


@app.before_request
def startup_save():
    """Save recommendations once on first request"""
    if not hasattr(app, '_recs_saved_today'):
        app._recs_saved_today = True
        # Run in background thread to not block request
        thread = threading.Thread(target=save_daily_recommendations, daemon=True)
        thread.start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

