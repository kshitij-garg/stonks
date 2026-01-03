/**
 * Stock API Client - Professional Trading Terminal
 * Complete API with watchlist, portfolio, compare, and backtesting
 */

const API_BASE = '/api';

// Main data endpoints
export async function fetchTopPerformers(timeframe = 'weekly') {
    const response = await fetch(`${API_BASE}/top-performers?timeframe=${timeframe}`);
    if (!response.ok) throw new Error('Failed to fetch top performers');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchProgress() {
    const response = await fetch(`${API_BASE}/progress`);
    if (!response.ok) return null;
    const data = await response.json();
    return data.data;
}

export async function fetchCacheStatus() {
    const response = await fetch(`${API_BASE}/cache-status`);
    if (!response.ok) return {};
    const data = await response.json();
    return data.data;
}

export async function triggerPrefetch() {
    const response = await fetch(`${API_BASE}/prefetch`, { method: 'POST' });
    return response.ok;
}

export async function fetchRecommendations(timeframe = 'weekly') {
    const response = await fetch(`${API_BASE}/recommendations?timeframe=${timeframe}`);
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchAllStocks(timeframe = 'weekly') {
    const response = await fetch(`${API_BASE}/all-stocks?timeframe=${timeframe}`);
    if (!response.ok) throw new Error('Failed to fetch stocks');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchStockDetails(symbol, period = '6mo') {
    const response = await fetch(`${API_BASE}/stock/${symbol}?period=${period}`);
    if (!response.ok) throw new Error(`Failed to fetch stock ${symbol}`);
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchMarketOverview() {
    const response = await fetch(`${API_BASE}/market-overview`);
    if (!response.ok) throw new Error('Failed to fetch market overview');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchSectors() {
    const response = await fetch(`${API_BASE}/sectors`);
    if (!response.ok) throw new Error('Failed to fetch sectors');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchScreenedStocks(filters = {}) {
    const params = new URLSearchParams();
    if (filters.minScore) params.append('min_score', filters.minScore);
    if (filters.minRsi) params.append('min_rsi', filters.minRsi);
    if (filters.maxRsi) params.append('max_rsi', filters.maxRsi);
    if (filters.sectors?.length) params.append('sectors', filters.sectors.join(','));
    if (filters.macd) params.append('macd', filters.macd);
    if (filters.valuation) params.append('valuation', filters.valuation);
    if (filters.minUpside) params.append('min_upside', filters.minUpside);
    if (filters.maxPe) params.append('max_pe', filters.maxPe);
    if (filters.timeframe) params.append('timeframe', filters.timeframe);

    const response = await fetch(`${API_BASE}/screener?${params}`);
    if (!response.ok) throw new Error('Failed to fetch screened stocks');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchStockUniverse() {
    const response = await fetch(`${API_BASE}/universe`);
    if (!response.ok) throw new Error('Failed to fetch universe');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

// Watchlist
export async function fetchWatchlist(watchlistId = 1) {
    const response = await fetch(`${API_BASE}/watchlist?id=${watchlistId}`);
    if (!response.ok) throw new Error('Failed to fetch watchlist');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function addToWatchlist(symbol, price = null) {
    const response = await fetch(`${API_BASE}/watchlist/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, price })
    });
    const data = await response.json();
    return data.success;
}

export async function removeFromWatchlist(symbol) {
    const response = await fetch(`${API_BASE}/watchlist/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
    });
    const data = await response.json();
    return data.success;
}

// Portfolio
export async function fetchPortfolio() {
    const response = await fetch(`${API_BASE}/portfolio`);
    if (!response.ok) throw new Error('Failed to fetch portfolio');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function addToPortfolio(symbol, quantity, price) {
    const response = await fetch(`${API_BASE}/portfolio/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, quantity, price })
    });
    const data = await response.json();
    return data.success;
}

export async function removeFromPortfolio(symbol) {
    const response = await fetch(`${API_BASE}/portfolio/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
    });
    const data = await response.json();
    return data.success;
}

// Compare
export async function fetchCompareStocks(symbols) {
    const response = await fetch(`${API_BASE}/compare?symbols=${symbols.join(',')}`);
    if (!response.ok) throw new Error('Failed to compare stocks');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

// Backtesting
export async function fetchBacktestResults(days = 30) {
    const response = await fetch(`${API_BASE}/backtest?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch backtest results');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return { data: data.data, stats: data.stats };
}

export async function saveRecommendationsSnapshot(timeframe = 'weekly') {
    const response = await fetch(`${API_BASE}/backtest/save?timeframe=${timeframe}`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to save snapshot');
    const data = await response.json();
    return data;
}
