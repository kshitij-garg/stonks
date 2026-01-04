# Known Limitations & Product Gaps

## 📊 Data Source Limitations

### yfinance Dependency
- **Delayed Data**: Data may be delayed by 15-20 minutes during market hours
- **No Real-time Streaming**: Requires manual refresh for latest prices
- **Rate Limiting**: Too many requests may get temporarily blocked
- **Missing Data**: Some less liquid stocks may have incomplete data
- **Yahoo Finance Changes**: API may break if Yahoo changes their structure

### Commodities Data
- **USD Conversion**: Gold/Silver prices are converted from USD futures, may not exactly match MCX India prices
- **No MCX Direct Feed**: Using international futures as proxy

## 🔮 Prediction Limitations

### DCF Valuation
- **Estimates Only**: Fair values are mathematical estimates, not guarantees
- **Growth Assumptions**: Uses conservative 8% discount rate, may not suit all stocks
- **Historical Bias**: Based on past performance which may not continue

### Recommendation Engine
- **Not Financial Advice**: Recommendations are algorithmic, not personalized
- **Lagging Indicators**: Technical indicators are based on past prices
- **No Fundamental Events**: Doesn't account for earnings surprises, news, etc.

### 1-Week Predictions
- **Directional Only**: Shows potential direction, not precise targets
- **Based on Momentum**: Assumes current trend continuation
- **High Uncertainty**: Short-term predictions are inherently unreliable

## 💼 Portfolio Features

### Missing Features
- **No Multi-portfolio Support**: Only one portfolio per instance
- **No Authentication**: Local SQLite storage, no cloud sync
- **No Transaction History**: Buy/sell tracking is basic
- **No Tax Calculations**: No capital gains or tax-loss harvesting
- **No XIRR**: Time-weighted returns not calculated yet

### CSV Import
- **Limited Brokers**: Currently supports Zerodha and Groww formats
- **Symbol Mapping**: Some stock symbols may need manual adjustment
- **No Auto-sync**: Manual import required, no broker API integration

## 📈 Technical Analysis

### Missing Indicators
- **Fibonacci Retracements**: Not implemented
- **Ichimoku Cloud**: Not available
- **Volume Profile**: Not available
- **Support/Resistance Levels**: Basic implementation only

### Chart Limitations
- **Line Charts Only**: No true candlestick rendering (Recharts limitation)
- **Limited Timeframes**: 1D, 1W, 1M periods only
- **No Drawing Tools**: Can't draw trendlines manually

## 🔔 Alerts

### Current Limitations
- **Browser Notification Only**: No email/SMS notifications
- **Polling Required**: Not real-time, need to check manually
- **No Push**: Background alerting not implemented

## 🏗️ Architecture Gaps

### Scalability
- **Single Threaded**: Flask development server, not production-ready
- **No Caching Layer**: Redis not implemented
- **SQLite**: Not suitable for multi-user deployment
- **No Rate Limiting**: Could be overwhelmed with requests

### Security
- **No User Authentication**: Anyone with access can see/modify data
- **No HTTPS**: Development server only
- **Session Token Only**: Basic session-based isolation

## 🌐 Deployment

### Not Production Ready
- **Development Server**: Flask development server shouldn't be used in production
- **No Docker**: Containerization not provided
- **No CI/CD**: Manual deployment required

## 📱 Mobile/UX

### Responsive Issues
- **Desktop First**: Mobile experience may be suboptimal
- **No PWA**: Not installable as app
- **No Offline Mode**: Requires constant internet connection

---

## 🚀 Roadmap (Future Improvements)

1. **Real-time Data**: WebSocket integration for live prices
2. **User Auth**: Login/signup with cloud sync
3. **Broker Integration**: Direct API connection to Zerodha/Groww
4. **Advanced Charts**: TradingView-style charting
5. **News & Sentiment**: Integrate financial news feeds
6. **Mobile App**: React Native version
7. **Options Data**: F&O analysis with Greeks
8. **Backtesting V2**: More sophisticated strategy testing

---

*Last Updated: January 2026*
