import { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Filter } from 'lucide-react';

function StockScreener({ stocks, isLoading, onStockClick }) {
    const [filters, setFilters] = useState({
        sector: 'all',
        marketCap: 'all',
        valuation: 'all',
        minScore: 0,
        maxPE: 100,
        macdSignal: 'all',
        sortBy: 'score'
    });

    const sectors = useMemo(() => {
        if (!stocks) return [];
        const sectorSet = new Set(stocks.map(s => s.sector));
        return Array.from(sectorSet).sort();
    }, [stocks]);

    const filteredStocks = useMemo(() => {
        if (!stocks) return [];

        return stocks
            .filter(stock => {
                // Sector filter
                if (filters.sector !== 'all' && stock.sector !== filters.sector) return false;

                // Market cap filter
                if (filters.marketCap !== 'all' && stock.market_cap_category !== filters.marketCap) return false;

                // Valuation filter
                if (filters.valuation !== 'all') {
                    const status = stock.valuation?.status?.toLowerCase() || '';
                    if (filters.valuation === 'undervalued' && !status.includes('undervalued')) return false;
                    if (filters.valuation === 'overvalued' && !status.includes('overvalued')) return false;
                    if (filters.valuation === 'fair' && !status.includes('fair')) return false;
                }

                // Score filter
                if (stock.scores.composite < filters.minScore) return false;

                // PE filter
                if (stock.fundamentals?.pe_ratio && stock.fundamentals.pe_ratio > filters.maxPE) return false;

                // MACD filter
                if (filters.macdSignal !== 'all' && stock.macd_signal !== filters.macdSignal) return false;

                return true;
            })
            .sort((a, b) => {
                switch (filters.sortBy) {
                    case 'score':
                        return b.scores.composite - a.scores.composite;
                    case 'pe':
                        return (a.fundamentals?.pe_ratio || 999) - (b.fundamentals?.pe_ratio || 999);
                    case 'change':
                        return b.change_percent - a.change_percent;
                    case 'valuation':
                        return (b.scores.valuation || 0) - (a.scores.valuation || 0);
                    default:
                        return 0;
                }
            });
    }, [stocks, filters]);

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(price);
    };

    const getValuationClass = (status) => {
        if (!status) return 'fair';
        const s = status.toLowerCase();
        if (s.includes('undervalued')) return 'undervalued';
        if (s.includes('overvalued')) return 'overvalued';
        return 'fair';
    };

    if (isLoading) {
        return (
            <div className="glass-card section">
                <div className="loading">
                    <div className="loading-spinner" />
                    <span className="loading-text">Loading stocks...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-card section">
            <div className="section-header">
                <h3 className="section-title">
                    <Filter size={20} />
                    Stock Screener
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Showing {filteredStocks.length} of {stocks?.length || 0} stocks
                </span>
            </div>

            {/* Filters */}
            <div className="filters">
                <div className="filter-group">
                    <label className="filter-label">Sector</label>
                    <select
                        className="filter-select"
                        value={filters.sector}
                        onChange={(e) => setFilters({ ...filters, sector: e.target.value })}
                    >
                        <option value="all">All Sectors</option>
                        {sectors.map(sector => (
                            <option key={sector} value={sector}>{sector}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Market Cap</label>
                    <select
                        className="filter-select"
                        value={filters.marketCap}
                        onChange={(e) => setFilters({ ...filters, marketCap: e.target.value })}
                    >
                        <option value="all">All</option>
                        <option value="Large Cap">Large Cap</option>
                        <option value="Mid Cap">Mid Cap</option>
                        <option value="Small Cap">Small Cap</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Valuation</label>
                    <select
                        className="filter-select"
                        value={filters.valuation}
                        onChange={(e) => setFilters({ ...filters, valuation: e.target.value })}
                    >
                        <option value="all">All</option>
                        <option value="undervalued">Undervalued</option>
                        <option value="fair">Fair Value</option>
                        <option value="overvalued">Overvalued</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Min Score</label>
                    <input
                        type="number"
                        className="filter-input"
                        value={filters.minScore}
                        onChange={(e) => setFilters({ ...filters, minScore: Number(e.target.value) })}
                        min={0}
                        max={100}
                        style={{ width: '80px' }}
                    />
                </div>

                <div className="filter-group">
                    <label className="filter-label">Max PE</label>
                    <input
                        type="number"
                        className="filter-input"
                        value={filters.maxPE}
                        onChange={(e) => setFilters({ ...filters, maxPE: Number(e.target.value) })}
                        min={0}
                        style={{ width: '80px' }}
                    />
                </div>

                <div className="filter-group">
                    <label className="filter-label">MACD Signal</label>
                    <select
                        className="filter-select"
                        value={filters.macdSignal}
                        onChange={(e) => setFilters({ ...filters, macdSignal: e.target.value })}
                    >
                        <option value="all">All</option>
                        <option value="Bullish">Bullish</option>
                        <option value="Bearish">Bearish</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Sort By</label>
                    <select
                        className="filter-select"
                        value={filters.sortBy}
                        onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                    >
                        <option value="score">Composite Score</option>
                        <option value="pe">PE Ratio (Low to High)</option>
                        <option value="change">% Change</option>
                        <option value="valuation">Valuation Score</option>
                    </select>
                </div>
            </div>

            {/* Stock List */}
            <div className="stock-list">
                {filteredStocks.map((stock, index) => (
                    <div
                        key={stock.symbol}
                        className="stock-card"
                        onClick={() => onStockClick(stock)}
                    >
                        <div className="stock-rank rank-default">
                            {index + 1}
                        </div>

                        <div className="stock-info">
                            <h4>{stock.symbol}</h4>
                            <span className="stock-name">{stock.name}</span>
                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                <span className="stock-sector">{stock.sector}</span>
                                <span className="stock-sector">{stock.market_cap_category}</span>
                                {stock.valuation?.status && (
                                    <span className={`valuation-badge ${getValuationClass(stock.valuation.status)}`}>
                                        {stock.valuation.status}
                                    </span>
                                )}
                                <span
                                    className="stock-sector"
                                    style={{
                                        background: stock.macd_signal === 'Bullish' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                        color: stock.macd_signal === 'Bullish' ? 'var(--accent-green)' : 'var(--accent-red)'
                                    }}
                                >
                                    MACD: {stock.macd_signal}
                                </span>
                            </div>
                        </div>

                        <div className="stock-price">
                            <div className="price">{formatPrice(stock.price)}</div>
                            <div className={`change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                {stock.change_percent >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                {stock.change_percent > 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                            </div>
                            <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                PE: {stock.fundamentals?.pe_ratio?.toFixed(1) || 'N/A'} | RSI: {stock.rsi?.toFixed(0) || 'N/A'}
                            </div>
                        </div>

                        <div className="stock-score">
                            <div
                                className="score-value"
                                style={{
                                    color: stock.scores.composite >= 60 ? 'var(--accent-green)' :
                                        stock.scores.composite >= 40 ? 'var(--accent-orange)' : 'var(--accent-red)'
                                }}
                            >
                                {stock.scores.composite.toFixed(0)}
                            </div>
                            <div className="score-label">Score</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default StockScreener;
