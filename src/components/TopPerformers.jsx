import { TrendingUp, TrendingDown, Award, AlertTriangle } from 'lucide-react';

function TopPerformers({ data, isLoading, error, onStockClick, type }) {
    const isTop = type === 'top';
    const stocks = isTop ? data?.top10 : data?.bottom10;
    const title = isTop ? 'Top 10 Best Performers' : 'Top 10 Worst Performers';
    const Icon = isTop ? Award : AlertTriangle;
    const iconColor = isTop ? '#10b981' : '#ef4444';

    if (isLoading) {
        return (
            <div className="section glass-card">
                <div className="section-header">
                    <h3 className="section-title">
                        <Icon size={20} color={iconColor} />
                        {title}
                    </h3>
                </div>
                <div className="loading">
                    <div className="loading-spinner" />
                    <p>Loading stocks...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="section glass-card">
                <div className="section-header">
                    <h3 className="section-title">
                        <Icon size={20} color={iconColor} />
                        {title}
                    </h3>
                </div>
                <div className="error">
                    Error loading data. Please refresh.
                </div>
            </div>
        );
    }

    if (!stocks?.length) {
        return (
            <div className="section glass-card">
                <div className="section-header">
                    <h3 className="section-title">
                        <Icon size={20} color={iconColor} />
                        {title}
                    </h3>
                </div>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                    No data available
                </p>
            </div>
        );
    }

    return (
        <div className="section glass-card">
            <div className="section-header">
                <h3 className="section-title">
                    <Icon size={20} color={iconColor} />
                    {title}
                </h3>
                <span className="badge">{data?.total_analyzed || 0} analyzed</span>
            </div>

            <div className="stock-list">
                {stocks.map((stock, i) => {
                    const rankClass = isTop
                        ? (i < 3 ? `rank-${i + 1}` : 'rank-default')
                        : 'rank-default';

                    return (
                        <div
                            key={stock.symbol}
                            className="stock-card"
                            onClick={() => onStockClick(stock)}
                        >
                            <div className={`stock-rank ${rankClass}`}>
                                {isTop ? i + 1 : stocks.length - i}
                            </div>

                            <div className="stock-info">
                                <h4>{stock.symbol}</h4>
                                <p className="stock-name">{stock.name}</p>
                                <div className="stock-badges">
                                    <span className="stock-sector">{stock.sector}</span>
                                    {stock.valuation_status && (
                                        <span className={`valuation-badge ${stock.valuation_status.toLowerCase().replace(' ', '-')}`}>
                                            {stock.valuation_status}
                                        </span>
                                    )}
                                </div>
                            </div>

                            <div className="stock-price">
                                <div className="price">₹{stock.price?.toLocaleString()}</div>
                                <div className={`change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                    {stock.change_percent >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                    {stock.change_percent?.toFixed(2)}%
                                </div>
                            </div>

                            <div className="stock-score">
                                <div className="score-value" style={{ color: getScoreColor(stock.scores?.composite) }}>
                                    {stock.scores?.composite?.toFixed(0)}
                                </div>
                                <div className="score-label">Score</div>
                                <div className="score-bar">
                                    <div
                                        className={`score-bar-fill ${getScoreClass(stock.scores?.composite)}`}
                                        style={{ width: `${stock.scores?.composite || 0}%` }}
                                    />
                                </div>
                            </div>

                            {/* DCF Indicator */}
                            {stock.dcf?.intrinsic_value > 0 && (
                                <div className="dcf-mini">
                                    <span className="dcf-label">DCF</span>
                                    <span className={`dcf-margin ${stock.dcf.margin_of_safety > 0 ? 'positive' : 'negative'}`}>
                                        {stock.dcf.margin_of_safety > 0 ? '+' : ''}{stock.dcf.margin_of_safety?.toFixed(0)}%
                                    </span>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function getScoreColor(score) {
    if (score >= 70) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
}

function getScoreClass(score) {
    if (score >= 70) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

export default TopPerformers;
