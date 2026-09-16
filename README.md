# QuantRebalance 📈⚖️

**Institutional-Grade Daily Portfolio Rebalancer & Equity Analysis Engine** for Indian Equities, Index & Sectoral ETFs, Mutual Funds, Commodities, and Liquid Arbitrage Reserves.

---

## 🌟 Key Features

### 1. 🔄 Multi-Strategy Institutional Rebalancing
- **Strategic Core-Satellite (Recommended)**:
  - 40% Core (Direct Bluechip Equities & Index ETFs)
  - 25% Satellite Alpha (Mid/Small Cap Equities & Mutual Funds)
  - 10% Commodities Hedge (Gold BeES, Silver ETF)
  - 25% Tactical Arbitrage & Liquid Buffer (Dry powder for market dips)
- **Aggressive Growth**: 55% Equities/ETFs, 25% Active MFs, 10% Gold, 10% Cash.
- **Conservative Wealth Preservation**: 40% Liquid Arbitrage Buffer, 15% Precious Metals, 45% High-Quality Bluechip Assets.
- **Custom Target Bounds**: Interactive allocation controls with real-time drift tracking.

### 2. 🛡️ Tax-Efficient Smart Cash Deployment
- **Zero Capital Gains Tax Mode**: Intelligently deploys dry powder from your liquid reserve (e.g., Kotak Arbitrage Fund) or fresh cash injections to purchase under-allocated assets.
- **Zero Unnecessary Churn**: Does not trigger capital gains tax from selling unless explicitly selected.
- **Drift Tolerance Filtering**: Configurable tolerance bands (±1% to ±8%) prevent over-trading on minor market fluctuations.

### 3. 📊 Real-Time Market Fundamentals & Technical Analytics
- **Live NSE/BSE Market Quotes**: Automated Yahoo Finance crumb authentication session for sub-second quote and OHLCV fetching.
- **AMFI Mutual Funds Integration**: Directly fetches daily NAVs and category tracking for all open-ended Indian mutual funds via `api.mfapi.in`.
- **Technical Analysis Engine**:
  - RSI (14-Day) momentum oscillator & oversold accumulation alerts.
  - Moving Averages: 20-Day, 50-Day, 200-Day SMA with Golden/Death Cross detection.
  - Dynamic 20-day swing support and resistance boundaries.
  - 52-Week High/Low range position.
- **Fundamental Multiples & Analyst Consensus**:
  - Trailing and Forward P/E multiples.
  - Market Capitalization, Profit Margins, Gross Margins, Debt/Equity.
  - Institutional Analyst coverage and consensus ratings (`Strong Buy`, `Buy`, `Hold`, `Sell`).
  - Analyst Consensus Price Targets (Mean, High, Low) with % upside calculation.

### 4. ⚡ 1-Click Trade Execution & Export
- **CSV Trade Sheet**: Direct download of calculated orders with exact quantities, rupee value, target prices, and stop losses.
- **Clipboard Export**: Instant copy to clipboard for rapid order placement on your broker terminal.

### 5. 📁 Daily Multi-Broker CSV Ingestion
- Auto-detects schemas from:
  - **Zerodha Kite** (Holdings & Tradebook)
  - **Groww** (Holdings export)
  - **Angel One**
  - **Upstox**
  - **ICICI Direct**
  - Standard Generic Broker CSVs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Python 3.10, 3.11, or 3.14)

### 1-Click Launch (Windows)
Double-click `start.bat` in the project folder:
```cmd
start.bat
```
This automatically starts the backend server on `http://127.0.0.1:5000` and opens your browser.

### 1-Click Launch (Linux / macOS)
```bash
chmod +x start.sh
./start.sh
```

### Manual Launch
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the application
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 📂 Project Architecture

```text
├── app.py                     # Flask REST API & Web Server
├── analyzer.py                # Technical & Fundamental Analysis Engine
├── rebalancer.py              # Portfolio Rebalancing & Allocation Math
├── csv_parser.py              # Universal Broker CSV Parser
├── test_integration.py        # Automated test verification suite
├── requirements.txt           # Python dependencies
├── start.bat                  # 1-click Windows launcher
├── start.sh                   # Unix/Linux launcher
├── data/
│   └── sample_holdings.csv    # Default/current portfolio state
├── docs/
│   └── ARCHIVE_V1.md          # Archive documentation for legacy v1 architecture
└── static/
    ├── index.html             # Institutional dark-theme terminal UI
    ├── styles.css             # Glassmorphism design system
    └── app.js                 # Chart.js analytics & dashboard logic
```

---

## 📖 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/portfolio` | GET | Returns current portfolio holdings, enriched live data, and KPI metrics |
| `POST /api/upload` | POST | Accepts multipart CSV or raw CSV body, parses holdings, updates state |
| `POST /api/rebalance` | POST | Executes rebalance simulation with selected strategy, tolerance, and inflow |
| `GET /api/deepdive/<symbol>` | GET | Returns full technical indicators, consensus targets, and trade plan for symbol |

---

## 🔒 Security & Privacy
- **100% Local**: All portfolio calculation and broker CSV parsing happens entirely on your local machine.
- No broker credentials, API keys, or personal identifiable information (PII) are ever transmitted to any external server.

---

## 📄 License & Archive
- MIT License - see [LICENSE](LICENSE).
- Legacy v1 documentation: [docs/ARCHIVE_V1.md](docs/ARCHIVE_V1.md).
- Legacy source code branch: `v1-legacy-backup` (tag `v1.0-legacy`).
