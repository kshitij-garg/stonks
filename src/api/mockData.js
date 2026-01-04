// Mock data for GitHub Pages static demo
// This provides sample data when the backend is not available

export const MOCK_DATA = {
    marketOverview: {
        indices: [
            { name: 'NIFTY 50', value: 24150.50, change: 125.30, change_percent: 0.52 },
            { name: 'SENSEX', value: 79850.25, change: 410.75, change_percent: 0.52 },
            { name: 'BANK NIFTY', value: 52340.80, change: -85.40, change_percent: -0.16 },
            { name: 'NIFTY IT', value: 41250.60, change: 320.15, change_percent: 0.78 }
        ],
        market_status: 'open',
        last_updated: new Date().toISOString()
    },

    topPerformers: {
        top: [
            { rank: 1, symbol: 'TATAELXSI', name: 'Tata Elxsi', price: 7850.50, change_percent: 4.25, sector: 'IT', scores: { composite: 78 }, rsi: 62, macd_signal: 'Bullish', recommendation: { action: 'STRONG BUY', upside: 18.5 }, dcf: { margin_of_safety: 12.5 } },
            { rank: 2, symbol: 'ADANIPORTS', name: 'Adani Ports', price: 1425.30, change_percent: 3.85, sector: 'Infrastructure', scores: { composite: 74 }, rsi: 58, macd_signal: 'Bullish', recommendation: { action: 'BUY', upside: 15.2 }, dcf: { margin_of_safety: 8.3 } },
            { rank: 3, symbol: 'BAJFINANCE', name: 'Bajaj Finance', price: 7125.80, change_percent: 3.42, sector: 'Financial', scores: { composite: 72 }, rsi: 55, macd_signal: 'Bullish', recommendation: { action: 'BUY', upside: 12.8 }, dcf: { margin_of_safety: 5.2 } },
            { rank: 4, symbol: 'INFY', name: 'Infosys', price: 1875.45, change_percent: 2.95, sector: 'IT', scores: { composite: 70 }, rsi: 52, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 8.5 }, dcf: { margin_of_safety: 3.1 } },
            { rank: 5, symbol: 'RELIANCE', name: 'Reliance Industries', price: 2950.60, change_percent: 2.78, sector: 'Energy', scores: { composite: 68 }, rsi: 48, macd_signal: 'Bullish', recommendation: { action: 'BUY', upside: 14.2 }, dcf: { margin_of_safety: 6.8 } },
            { rank: 6, symbol: 'TCS', name: 'TCS', price: 4125.30, change_percent: 2.55, sector: 'IT', scores: { composite: 67 }, rsi: 51, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 7.5 }, dcf: { margin_of_safety: 2.5 } },
            { rank: 7, symbol: 'HDFCBANK', name: 'HDFC Bank', price: 1725.80, change_percent: 2.35, sector: 'Banking', scores: { composite: 65 }, rsi: 49, macd_signal: 'Bullish', recommendation: { action: 'BUY', upside: 11.2 }, dcf: { margin_of_safety: 4.8 } },
            { rank: 8, symbol: 'ICICIBANK', name: 'ICICI Bank', price: 1285.45, change_percent: 2.12, sector: 'Banking', scores: { composite: 64 }, rsi: 47, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 9.5 }, dcf: { margin_of_safety: 3.2 } },
            { rank: 9, symbol: 'WIPRO', name: 'Wipro', price: 485.60, change_percent: 1.95, sector: 'IT', scores: { composite: 62 }, rsi: 45, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 6.8 }, dcf: { margin_of_safety: 1.5 } },
            { rank: 10, symbol: 'LT', name: 'Larsen & Toubro', price: 3650.25, change_percent: 1.78, sector: 'Infrastructure', scores: { composite: 61 }, rsi: 44, macd_signal: 'Bullish', recommendation: { action: 'BUY', upside: 10.5 }, dcf: { margin_of_safety: 5.5 } }
        ],
        bottom: [
            { rank: 1, symbol: 'TATASTEEL', name: 'Tata Steel', price: 142.50, change_percent: -3.85, sector: 'Metals', scores: { composite: 32 }, rsi: 28, macd_signal: 'Bearish', recommendation: { action: 'SELL', upside: -8.5 }, dcf: { margin_of_safety: -15.2 } },
            { rank: 2, symbol: 'HINDALCO', name: 'Hindalco', price: 625.30, change_percent: -3.25, sector: 'Metals', scores: { composite: 35 }, rsi: 32, macd_signal: 'Bearish', recommendation: { action: 'SELL', upside: -6.2 }, dcf: { margin_of_safety: -12.5 } },
            { rank: 3, symbol: 'JSWSTEEL', name: 'JSW Steel', price: 875.45, change_percent: -2.95, sector: 'Metals', scores: { composite: 38 }, rsi: 35, macd_signal: 'Bearish', recommendation: { action: 'SELL', upside: -5.8 }, dcf: { margin_of_safety: -10.2 } },
            { rank: 4, symbol: 'COALINDIA', name: 'Coal India', price: 425.60, change_percent: -2.45, sector: 'Mining', scores: { composite: 40 }, rsi: 38, macd_signal: 'Bearish', recommendation: { action: 'HOLD', upside: -2.5 }, dcf: { margin_of_safety: -5.8 } },
            { rank: 5, symbol: 'ONGC', name: 'ONGC', price: 265.80, change_percent: -2.15, sector: 'Energy', scores: { composite: 42 }, rsi: 40, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: -1.2 }, dcf: { margin_of_safety: -3.5 } },
            { rank: 6, symbol: 'BPCL', name: 'BPCL', price: 315.25, change_percent: -1.95, sector: 'Energy', scores: { composite: 43 }, rsi: 41, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 1.5 }, dcf: { margin_of_safety: -2.8 } },
            { rank: 7, symbol: 'IOC', name: 'Indian Oil', price: 145.60, change_percent: -1.75, sector: 'Energy', scores: { composite: 44 }, rsi: 42, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 2.8 }, dcf: { margin_of_safety: -1.5 } },
            { rank: 8, symbol: 'NTPC', name: 'NTPC', price: 385.30, change_percent: -1.55, sector: 'Power', scores: { composite: 45 }, rsi: 43, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 3.5 }, dcf: { margin_of_safety: 0.5 } },
            { rank: 9, symbol: 'POWERGRID', name: 'Power Grid', price: 285.45, change_percent: -1.35, sector: 'Power', scores: { composite: 46 }, rsi: 44, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 4.2 }, dcf: { margin_of_safety: 1.2 } },
            { rank: 10, symbol: 'GAIL', name: 'GAIL', price: 195.80, change_percent: -1.15, sector: 'Energy', scores: { composite: 47 }, rsi: 45, macd_signal: 'Neutral', recommendation: { action: 'HOLD', upside: 5.0 }, dcf: { margin_of_safety: 2.0 } }
        ],
        total_analyzed: 135,
        timestamp: new Date().toISOString()
    },

    sectors: [
        { name: 'IT', change_percent: 2.15, stocks: ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'] },
        { name: 'Banking', change_percent: 1.85, stocks: ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN'] },
        { name: 'Financial', change_percent: 1.65, stocks: ['BAJFINANCE', 'BAJAJFINSV', 'HDFC', 'SBILIFE', 'HDFCLIFE'] },
        { name: 'Auto', change_percent: 0.95, stocks: ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO'] },
        { name: 'Pharma', change_percent: 0.55, stocks: ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'APOLLOHOSP'] },
        { name: 'Energy', change_percent: -0.45, stocks: ['RELIANCE', 'ONGC', 'BPCL', 'IOC', 'GAIL'] },
        { name: 'Metals', change_percent: -2.35, stocks: ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'NMDC'] },
        { name: 'FMCG', change_percent: 0.35, stocks: ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'] }
    ],

    commodities: [
        { symbol: 'GOLD', name: 'Gold', price: 62450, change_1w: 1.25, change_1m: 2.85, unit: '₹/10g' },
        { symbol: 'SILVER', name: 'Silver', price: 74850, change_1w: 2.15, change_1m: 4.35, unit: '₹/kg' },
        { symbol: 'CRUDE', name: 'Crude Oil', price: 6125, change_1w: -1.85, change_1m: -3.25, unit: '₹/barrel' }
    ],

    recommendations: {
        summary: { strong_buy: 12, buy: 35, hold: 58, sell: 22, strong_sell: 8 },
        top_picks: [
            { symbol: 'TATAELXSI', name: 'Tata Elxsi', price: 7850.50, change_percent: 4.25, sector: 'IT', recommendation: { action: 'STRONG BUY', upside: 18.5, confidence: 82 }, dcf: { margin_of_safety: 12.5 } },
            { symbol: 'ADANIPORTS', name: 'Adani Ports', price: 1425.30, change_percent: 3.85, sector: 'Infrastructure', recommendation: { action: 'STRONG BUY', upside: 15.2, confidence: 78 }, dcf: { margin_of_safety: 8.3 } },
            { symbol: 'BAJFINANCE', name: 'Bajaj Finance', price: 7125.80, change_percent: 3.42, sector: 'Financial', recommendation: { action: 'BUY', upside: 12.8, confidence: 75 }, dcf: { margin_of_safety: 5.2 } },
            { symbol: 'RELIANCE', name: 'Reliance Industries', price: 2950.60, change_percent: 2.78, sector: 'Energy', recommendation: { action: 'BUY', upside: 14.2, confidence: 72 }, dcf: { margin_of_safety: 6.8 } },
            { symbol: 'HDFCBANK', name: 'HDFC Bank', price: 1725.80, change_percent: 2.35, sector: 'Banking', recommendation: { action: 'BUY', upside: 11.2, confidence: 70 }, dcf: { margin_of_safety: 4.8 } }
        ],
        avoid_list: [
            { symbol: 'TATASTEEL', name: 'Tata Steel', price: 142.50, change_percent: -3.85, sector: 'Metals', recommendation: { action: 'STRONG SELL', upside: -8.5 } },
            { symbol: 'HINDALCO', name: 'Hindalco', price: 625.30, change_percent: -3.25, sector: 'Metals', recommendation: { action: 'SELL', upside: -6.2 } },
            { symbol: 'JSWSTEEL', name: 'JSW Steel', price: 875.45, change_percent: -2.95, sector: 'Metals', recommendation: { action: 'SELL', upside: -5.8 } }
        ]
    }
};

// Check if we're in demo mode (no backend)
export const isDemoMode = () => {
    return window.location.hostname.includes('github.io') ||
        window.location.hostname.includes('pages.dev') ||
        localStorage.getItem('DEMO_MODE') === 'true';
};
