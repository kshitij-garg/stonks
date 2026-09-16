import os
import io
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

from csv_parser import parse_holdings_csv
from analyzer import MarketAnalyzer
from rebalancer import PortfolioRebalancer, STRATEGIES

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("QuantRebalance")

app = Flask(__name__, static_folder="static", static_url_path="")
if CORS:
    CORS(app)

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOLDINGS_FILE = os.path.join(BASE_DIR, "data", "sample_holdings.csv")

analyzer = MarketAnalyzer()
rebalancer = PortfolioRebalancer()

cached_portfolio = {
    "raw_holdings": [],
    "enriched_holdings": [],
    "metrics": {},
    "last_synced": None
}

def load_initial_holdings():
    if os.path.exists(HOLDINGS_FILE):
        try:
            with open(HOLDINGS_FILE, "r", encoding="utf-8") as f:
                csv_content = f.read()
            raw = parse_holdings_csv(csv_content)
            enriched = analyzer.analyze_portfolio(raw)
            metrics = rebalancer.compute_portfolio_metrics(enriched)
            cached_portfolio["raw_holdings"] = raw
            cached_portfolio["enriched_holdings"] = enriched
            cached_portfolio["metrics"] = metrics
            cached_portfolio["last_synced"] = datetime.now().strftime("%d %b %Y, %H:%M:%S IST")
            logger.info(f"Loaded {len(enriched)} initial holdings.")
        except Exception as e:
            logger.error(f"Error loading initial holdings: {e}")

# Pre-load holdings
load_initial_holdings()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "QuantRebalance Portfolio Engine",
        "timestamp": datetime.now().isoformat(),
        "holdings_count": len(cached_portfolio["enriched_holdings"])
    })

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    refresh = request.args.get("refresh", "false").lower() == "true"
    if refresh or not cached_portfolio["enriched_holdings"]:
        load_initial_holdings()
        
    return jsonify({
        "success": True,
        "metrics": cached_portfolio["metrics"],
        "holdings": cached_portfolio["enriched_holdings"],
        "strategies": STRATEGIES,
        "last_synced": cached_portfolio["last_synced"]
    })

@app.route("/api/upload", methods=["POST"])
def upload_csv():
    try:
        csv_text = None
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                csv_text = file.read().decode("utf-8-sig", errors="replace")
        elif request.is_json:
            csv_text = request.json.get("csv_content")
        elif request.data:
            csv_text = request.data.decode("utf-8-sig", errors="replace")

        if not csv_text:
            return jsonify({"success": False, "error": "No CSV content provided"}), 400

        raw = parse_holdings_csv(csv_text)
        if not raw:
            return jsonify({"success": False, "error": "Could not parse valid holdings. Please verify CSV column headers."}), 400

        # Save uploaded file
        os.makedirs(os.path.dirname(HOLDINGS_FILE), exist_ok=True)
        with open(HOLDINGS_FILE, "w", encoding="utf-8") as f:
            f.write(csv_text)

        enriched = analyzer.analyze_portfolio(raw)
        metrics = rebalancer.compute_portfolio_metrics(enriched)
        
        cached_portfolio["raw_holdings"] = raw
        cached_portfolio["enriched_holdings"] = enriched
        cached_portfolio["metrics"] = metrics
        cached_portfolio["last_synced"] = datetime.now().strftime("%d %b %Y, %H:%M:%S IST")

        return jsonify({
            "success": True,
            "message": f"Successfully parsed and analyzed {len(raw)} holdings.",
            "metrics": metrics,
            "holdings": enriched,
            "last_synced": cached_portfolio["last_synced"]
        })
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/rebalance", methods=["POST"])
def rebalance():
    try:
        data = request.get_json() or {}
        strategy_key = data.get("strategy_key", "core_satellite")
        rebalance_mode = data.get("rebalance_mode", "smart_inflow")
        fresh_capital = float(data.get("fresh_capital", 0.0))
        tolerance_band = float(data.get("tolerance_band", 3.0))
        custom_targets = data.get("custom_targets")

        if not cached_portfolio["enriched_holdings"]:
            load_initial_holdings()

        plan = rebalancer.generate_rebalance_plan(
            cached_portfolio["enriched_holdings"],
            strategy_key=strategy_key,
            rebalance_mode=rebalance_mode,
            fresh_capital=fresh_capital,
            tolerance_band=tolerance_band,
            custom_targets=custom_targets
        )

        return jsonify({
            "success": True,
            "plan": plan
        })
    except Exception as e:
        logger.error(f"Rebalance error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/deepdive/<symbol>", methods=["GET"])
def deepdive(symbol):
    try:
        matching = [
            h for h in cached_portfolio["enriched_holdings"]
            if h.get("instrument") == symbol or h.get("ticker") == symbol or (h.get("ticker") and h.get("ticker").startswith(symbol))
        ]
        if not matching:
            return jsonify({"success": False, "error": f"Instrument '{symbol}' not found in holdings"}), 404

        holding = matching[0]
        ticker = holding.get("ticker")
        tech = analyzer.fetch_technical_data(ticker) if ticker else None
        fund = analyzer.fetch_fundamental_data(ticker) if (ticker and holding.get("is_equity")) else None
        mf_info = analyzer.fetch_mf_data(holding.get("instrument", "")) if holding.get("is_mf") else None

        return jsonify({
            "success": True,
            "instrument": holding.get("instrument"),
            "holding": holding,
            "technical": tech,
            "fundamental": fund,
            "mf_info": mf_info,
            "analysis": holding.get("analysis")
        })
    except Exception as e:
        logger.error(f"Deepdive error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/export-basket", methods=["POST"])
def export_basket():
    try:
        data = request.get_json() or {}
        basket_orders = data.get("basket_orders", [])
        return Response(
            json.dumps(basket_orders, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=zerodha_basket_orders.json"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  QuantRebalance Institutional Engine running on:")
    print(f"  -> Local URL: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
