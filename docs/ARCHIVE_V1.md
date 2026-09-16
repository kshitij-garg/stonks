# Stonks v1 Legacy Archive & Architectural Retrospective

> **Archive Tag**: `v1.0-legacy` | **Archive Branch**: `v1-legacy-backup`  
> **Development Period**: January 2026 | **Author**: Kshitij Garg (KG)

---

## 1. Overview of Version 1.0 (Legacy)

Stonks v1 was developed in January 2026 as a multi-tier Indian stock screener and market analytics application. It was composed of two separate runtime processes:
1. **Frontend**: A React 18 single-page application bundled with Vite and TailwindCSS/Vanilla CSS.
2. **Backend**: A Python FastAPI server providing REST endpoints for NIFTY 50 equities, yfinance queries, DCF valuations, and commodity prices.

---

## 2. Legacy Architecture & Endpoints

### Frontend (React + Vite)
- Located in `src/` with components including:
  - `Header.jsx`, `SearchBar.jsx`, `StockCard.jsx`, `StockChart.jsx`
  - Views: Top Performers, Recommendations, Screener, DCF Valuation, Commodities, Portfolio, Backtest History
- Port: `5173` (Vite dev server)

### Backend (FastAPI)
- Located in `backend/` with services:
  - `backend/services/stock_service.py`: Market data and indicators via yfinance
  - `backend/services/stock_universe.py`: NIFTY 50 and custom universe definition
  - `backend/services/dcf.py`: Discounted Cash Flow valuation calculations
  - `backend/services/portfolio.py`: Holdings tracker
  - `backend/services/commodities.py`: Gold, Silver, and Crude Oil spot tracking
  - `backend/services/backtest.py`: Historical recommendation performance tracker
- Port: `5000` (FastAPI / Uvicorn server)

### Core Endpoints in v1
- `GET /api/top-performers`: Top gainers/losers across NIFTY 50
- `GET /api/recommendations`: Multi-factor buy/sell recommendations
- `GET /api/stock/{symbol}`: Stock detail and indicator values
- `GET /api/screener`: Screener filters (RSI, PE, market cap)
- `GET /api/dcf/{symbol}`: Discounted Cash Flow fair value estimates
- `GET /api/commodities`: Gold, Silver, Crude Oil spot prices
- `GET /api/search`: Fuzzy stock search with autocomplete
- `GET /api/backtest/history`: Date-wise historical recommendation logs

---

## 3. Rationale for Migration to v2 (QuantRebalance)

While v1 functioned as a broad market screener, real-world portfolio management required a specialized, zero-friction workflow:
1. **Dual-Server Overhead**: Running both Node.js (Vite) and Python (FastAPI) created unnecessary dependency bloat (`node_modules/`, Python virtual environment conflicts, cross-origin port issues).
2. **Shift to Portfolio Rebalancing**: Investors needed a tool focused on their actual holdings (Equities, ETFs, Mutual Funds, Commodities, Arbitrage/Liquid funds), daily broker CSV uploads, and actionable order generation.
3. **Tax-Efficient Cash Deployment**: The Indian tax regime (STCG @ 20%, LTCG @ 12.5%) makes frequent selling of equities costly. Version 2 introduces strategic inflow rebalancing that deploys capital from arbitrage buffers (e.g. Kotak Arbitrage Fund) into oversold assets without triggering taxable events.
4. **Unified Single-Stack Architecture**: Version 2 runs entirely through a single lightweight Python service with a zero-build, institutional dark-theme dashboard powered by vanilla CSS and Chart.js.

---

## 4. Accessing Legacy v1 Code

The complete legacy v1 source code, history, and documentation are permanently preserved in Git:
- **Git Branch**: `git checkout v1-legacy-backup`
- **Git Tag**: `git checkout v1.0-legacy`
