/**
 * Stock API Client - Complete Professional Trading Terminal
 * Supports demo mode with mock data for GitHub Pages
 */

import { MOCK_DATA, isDemoMode } from './mockData';

const API_BASE = '/api';

// Check if we're in demo mode
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true' || isDemoMode();

// Main data endpoints
export async function fetchTopPerformers(timeframe = 'weekly') {
    if (DEMO_MODE) {
        return MOCK_DATA.topPerformers;
    }
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

export async function importPortfolioCSV(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/portfolio/import`, {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    return data;
}

export async function clearPortfolio() {
    const response = await fetch(`${API_BASE}/portfolio/clear`, { method: 'POST' });
    const data = await response.json();
    return data.success;
}

export async function fetchPortfolioAnalytics(timeframe = 'weekly') {
    const response = await fetch(`${API_BASE}/portfolio/analytics?timeframe=${timeframe}`);
    if (!response.ok) throw new Error('Failed to fetch portfolio analytics');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
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

// =============================================
// COMMODITIES
// =============================================

export async function fetchCommodities() {
    const response = await fetch(`${API_BASE}/commodities`);
    if (!response.ok) throw new Error('Failed to fetch commodities');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchCommodity(symbol, period = '6mo') {
    const response = await fetch(`${API_BASE}/commodity/${symbol}?period=${period}`);
    if (!response.ok) throw new Error('Failed to fetch commodity');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchMarketSummary() {
    const response = await fetch(`${API_BASE}/market-summary`);
    if (!response.ok) throw new Error('Failed to fetch market summary');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

// =============================================
// ALERTS
// =============================================

export async function fetchAlerts(symbol = null) {
    const url = symbol ? `${API_BASE}/alerts?symbol=${symbol}` : `${API_BASE}/alerts`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function createAlert(symbol, targetPrice, condition = 'above', notes = '') {
    const response = await fetch(`${API_BASE}/alerts/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, target_price: targetPrice, condition, notes })
    });
    const data = await response.json();
    return data;
}

export async function deleteAlert(alertId) {
    const response = await fetch(`${API_BASE}/alerts/${alertId}/delete`, { method: 'POST' });
    const data = await response.json();
    return data.success;
}

export async function checkAlerts() {
    const response = await fetch(`${API_BASE}/alerts/check`, { method: 'POST' });
    const data = await response.json();
    return data;
}

export async function fetchAlertHistory(limit = 50) {
    const response = await fetch(`${API_BASE}/alerts/history?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch alert history');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

// =============================================
// FUNDAMENTALS
// =============================================

export async function fetchFundamentals(symbol) {
    const response = await fetch(`${API_BASE}/fundamentals/${symbol}`);
    if (!response.ok) throw new Error('Failed to fetch fundamentals');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchQuarterlyResults(symbol) {
    const response = await fetch(`${API_BASE}/fundamentals/${symbol}/quarterly`);
    if (!response.ok) throw new Error('Failed to fetch quarterly results');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchBalanceSheet(symbol) {
    const response = await fetch(`${API_BASE}/fundamentals/${symbol}/balance-sheet`);
    if (!response.ok) throw new Error('Failed to fetch balance sheet');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

export async function fetchPeerComparison(symbol) {
    const response = await fetch(`${API_BASE}/fundamentals/${symbol}/peers`);
    if (!response.ok) throw new Error('Failed to fetch peer comparison');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}

// =============================================
// CHART DATA
// =============================================

export async function fetchChartData(symbol, period = '6mo', interval = '1d') {
    const response = await fetch(`${API_BASE}/chart/${symbol}?period=${period}&interval=${interval}`);
    if (!response.ok) throw new Error('Failed to fetch chart data');
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'API error');
    return data.data;
}
