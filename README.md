# Stonks by KG 📈🚀

A professional-grade stock analysis and portfolio tracking application for Indian markets (NSE/BSE). Features technical analysis, DCF valuation, AI-powered recommendations, and real-time commodity tracking.

![Stocks](https://img.shields.io/badge/Stocks-135+-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18+-cyan)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red)

## ✨ Features

### 📊 Dashboard
- Market indices (NIFTY 50, SENSEX, BANK NIFTY)
- Commodities tracking (Gold, Silver, Crude Oil)
- Top/Bottom performers with scoring
- Sector heatmap

### 🎯 Recommendations Engine
- Multi-factor scoring (momentum, technical, trend, volume)
- DCF valuation with margin of safety
- STRONG BUY → STRONG SELL ratings
- Confidence scores and target prices

### 📈 Technical Analysis
- RSI, MACD, Bollinger Bands, ATR
- Moving Averages (SMA 20/50, EMA)
- Pattern detection (Golden Cross, Death Cross, etc.)
- Interactive charts with indicator overlays

### 💼 Portfolio Management
- Import holdings from Zerodha/Groww CSV
- Real-time P&L tracking
- Sector allocation visualization
- 1-week upside predictions
- Risk assessment and concentration warnings

### 🔔 Price Alerts
- Set above/below target alerts
- Alert history tracking
- Persistent storage

### 📋 Additional Features
- Stock screener with 10+ filters
- Watchlist management
- Stock comparison (up to 5 stocks)
- Fundamentals (quarterly results, balance sheet, peer comparison)
- Backtesting framework
- **Quick search with autocomplete** (any ticker)

## 🌐 Live Demo

Try the static demo (with sample data): **https://kshitij-garg.github.io/stonks/**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### One-Click Setup (Windows)

1. **Clone the repository**
```bash
git clone https://github.com/kshitij-garg/stonks.git
cd stonks
```

2. **Run setup script** (installs all dependencies)
```bash
setup.bat
```

3. **Start the application**
```bash
start.bat
```

The browser will open automatically at `http://localhost:5173`

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

1. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Install frontend dependencies**
```bash
cd ..
npm install
```

3. **Start backend server**
```bash
cd backend
py -3 main.py
```

4. **Start frontend (new terminal)**
```bash
npm run dev
```

5. **Open browser**: http://localhost:5173

</details>


## 📁 Project Structure

```
Stonks/
├── backend/
│   ├── main.py              # Flask application entry
│   ├── requirements.txt     # Python dependencies
│   ├── routes/
│   │   └── api.py          # REST API endpoints
│   ├── services/
│   │   ├── stock_service.py    # Stock data fetching
│   │   ├── stock_universe.py   # NIFTY 50/Next 50/Midcap 50
│   │   ├── indicators.py       # Technical indicators
│   │   ├── scoring.py          # Stock scoring & recommendations
│   │   ├── valuation.py        # DCF valuation
│   │   ├── patterns.py         # Chart patterns
│   │   ├── portfolio.py        # Portfolio management
│   │   ├── watchlist.py        # Watchlist service
│   │   ├── alerts.py           # Price alerts
│   │   ├── commodities.py      # Gold/Silver/Crude
│   │   ├── fundamentals.py     # Quarterly/Balance sheet
│   │   └── csv_import.py       # Zerodha/Groww import
│   └── data/                # SQLite databases (gitignored)
├── src/
│   ├── App.jsx             # Main React component
│   ├── api/
│   │   └── stockApi.js     # API client
│   └── components/
│       ├── Dashboard components
│       ├── Portfolio.jsx
│       ├── StockChart.jsx
│       └── ...
├── index.html
├── vite.config.js
└── package.json
```

## 🔧 Configuration

### Environment Variables (optional)
Create a `.env` file in the root:
```
FLASK_DEBUG=1
FLASK_PORT=5000
```

### Stock Universe
Edit `backend/services/stock_universe.py` to add/remove stocks.

## 📖 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/top-performers` | GET | Top 10 best/worst stocks |
| `/api/recommendations` | GET | Buy/Sell recommendations |
| `/api/stock/<symbol>` | GET | Stock detail with indicators |
| `/api/screener` | GET | Filter stocks by criteria |
| `/api/portfolio` | GET | Portfolio summary |
| `/api/portfolio/analytics` | GET | Portfolio insights & predictions |
| `/api/commodities` | GET | Gold, Silver, Crude prices |
| `/api/alerts` | GET | Active price alerts |
| `/api/chart/<symbol>` | GET | OHLC with indicators |

## ⚠️ Limitations

See [LIMITATIONS.md](LIMITATIONS.md) for detailed limitations and known issues.

**Key Limitations:**
- Data sourced from yfinance (may have delays)
- DCF valuations are estimates, not financial advice
- Predictions are based on historical patterns
- No real-time streaming data

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

## ⚠️ Disclaimer

This software is for **educational purposes only**. It is not financial advice. Always do your own research and consult a qualified financial advisor before making investment decisions.

---

Built with ❤️ by **KG** for the Indian investor community
