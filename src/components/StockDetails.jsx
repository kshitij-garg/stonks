import { X, TrendingUp, TrendingDown, Target, DollarSign, Activity, BarChart2 } from 'lucide-react';

function StockDetails({ stock, onClose }) {
    if (!stock) return null;

    const formatPrice = (price) => {
        if (!price && price !== 0) return 'N/A';
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(price);
    };

    const formatNumber = (num) => {
        if (!num && num !== 0) return 'N/A';
        if (num >= 10000000) {
            return `₹${(num / 10000000).toFixed(2)} Cr`;
        }
        if (num >= 100000) {
            return `₹${(num / 100000).toFixed(2)} L`;
        }
        return num.toFixed(2);
    };

    const getValuationClass = (status) => {
        if (!status) return 'fair';
        const s = status.toLowerCase();
        if (s.includes('undervalued')) return 'undervalued';
        if (s.includes('overvalued')) return 'overvalued';
        return 'fair';
    };

    const targets = stock.targets || {};
    const fundamentals = stock.fundamentals || {};
    const signals = stock.signals || {};
    const scores = stock.scores || {};
    const returns = stock.returns || {};

    return (
        <div className={`stock-details ${stock ? 'open' : ''}`}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                <div>
                    <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{stock.symbol}</h2>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{stock.name}</p>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                        <span className="stock-sector">{stock.sector}</span>
                        <span className="stock-sector">{stock.market_cap_category}</span>
                        {stock.valuation?.status && (
                            <span className={`valuation-badge ${getValuationClass(stock.valuation.status)}`}>
                                {stock.valuation.status}
                            </span>
                        )}
                    </div>
                </div>
                <button
                    onClick={onClose}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        padding: '0.5rem'
                    }}
                >
                    <X size={24} />
                </button>
            </div>

            {/* Price */}
            <div style={{
                padding: '1.25rem',
                background: 'var(--bg-glass)',
                borderRadius: 'var(--border-radius)',
                marginBottom: '1rem'
            }}>
                <div style={{ fontSize: '2rem', fontWeight: '700' }}>{formatPrice(stock.price)}</div>
                <div className={`change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`} style={{ fontSize: '1rem', marginTop: '0.25rem' }}>
                    {stock.change_percent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    <span style={{ marginLeft: '0.5rem' }}>
                        {stock.change_percent > 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}% today
                    </span>
                </div>
            </div>

            {/* Composite Score */}
            <div style={{
                padding: '1.25rem',
                background: 'var(--bg-glass)',
                borderRadius: 'var(--border-radius)',
                marginBottom: '1rem'
            }}>
                <h4 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <BarChart2 size={18} /> Score Breakdown
                </h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Composite</span>
                    <span style={{
                        fontSize: '1.5rem',
                        fontWeight: '700',
                        color: scores.composite >= 60 ? 'var(--accent-green)' : scores.composite >= 40 ? 'var(--accent-orange)' : 'var(--accent-red)'
                    }}>
                        {scores.composite?.toFixed(1)}
                    </span>
                </div>
                <div className="score-bar" style={{ marginBottom: '1rem' }}>
                    <div
                        className={`score-bar-fill ${scores.composite >= 60 ? 'high' : scores.composite >= 40 ? 'medium' : 'low'}`}
                        style={{ width: `${scores.composite}%` }}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                    {[
                        { label: 'Momentum', value: scores.momentum },
                        { label: 'Technical', value: scores.technical },
                        { label: 'Volume', value: scores.volume },
                        { label: 'Trend', value: scores.trend },
                        { label: 'Valuation', value: scores.valuation },
                        { label: 'PE Score', value: scores.pe_score }
                    ].map(({ label, value }) => (
                        <div key={label} className="metric">
                            <div className="metric-value">{value?.toFixed(0) || 'N/A'}</div>
                            <div className="metric-label">{label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Target Prices */}
            {targets.current_price && (
                <div style={{
                    padding: '1.25rem',
                    background: 'var(--bg-glass)',
                    borderRadius: 'var(--border-radius)',
                    marginBottom: '1rem'
                }}>
                    <h4 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Target size={18} /> Target Prices
                    </h4>

                    <div className="targets-container">
                        <div className="target-box buy">
                            <div className="target-label">Buy Target 1</div>
                            <div className="target-value" style={{ color: 'var(--accent-green)' }}>
                                {formatPrice(targets.buy_targets?.conservative)}
                            </div>
                            <div className="target-percent">
                                -{targets.downside_risk?.conservative?.toFixed(1)}% downside
                            </div>
                        </div>
                        <div className="target-box sell">
                            <div className="target-label">Sell Target 1</div>
                            <div className="target-value" style={{ color: 'var(--accent-red)' }}>
                                {formatPrice(targets.sell_targets?.conservative)}
                            </div>
                            <div className="target-percent">
                                +{targets.upside_potential?.conservative?.toFixed(1)}% upside
                            </div>
                        </div>
                        <div className="target-box buy">
                            <div className="target-label">Buy Target 2</div>
                            <div className="target-value" style={{ color: 'var(--accent-green)' }}>
                                {formatPrice(targets.buy_targets?.aggressive)}
                            </div>
                            <div className="target-percent">
                                -{targets.downside_risk?.aggressive?.toFixed(1)}% downside
                            </div>
                        </div>
                        <div className="target-box sell">
                            <div className="target-label">Sell Target 2</div>
                            <div className="target-value" style={{ color: 'var(--accent-red)' }}>
                                {formatPrice(targets.sell_targets?.aggressive)}
                            </div>
                            <div className="target-percent">
                                +{targets.upside_potential?.aggressive?.toFixed(1)}% upside
                            </div>
                        </div>
                    </div>

                    <div style={{
                        marginTop: '1rem',
                        padding: '0.75rem',
                        background: targets.risk_reward_ratio >= 2 ? 'rgba(16, 185, 129, 0.1)' :
                            targets.risk_reward_ratio >= 1 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        borderRadius: 'var(--border-radius)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Risk/Reward Ratio</span>
                        <span style={{
                            fontWeight: '700',
                            color: targets.risk_reward_ratio >= 2 ? 'var(--accent-green)' :
                                targets.risk_reward_ratio >= 1 ? 'var(--accent-orange)' : 'var(--accent-red)'
                        }}>
                            {targets.risk_reward_ratio?.toFixed(2)} ({targets.recommendation})
                        </span>
                    </div>
                </div>
            )}

            {/* Fundamentals */}
            <div style={{
                padding: '1.25rem',
                background: 'var(--bg-glass)',
                borderRadius: 'var(--border-radius)',
                marginBottom: '1rem'
            }}>
                <h4 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <DollarSign size={18} /> Fundamentals
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>PE Ratio</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{fundamentals.pe_ratio?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>P/B Ratio</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{fundamentals.pb_ratio?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>EPS</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{fundamentals.eps?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>ROE</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{fundamentals.roe ? `${fundamentals.roe.toFixed(1)}%` : 'N/A'}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>52W High</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{formatPrice(fundamentals['52w_high'])}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>52W Low</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{formatPrice(fundamentals['52w_low'])}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Market Cap</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{formatNumber(stock.market_cap)}</div>
                    </div>
                    <div>
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Div Yield</div>
                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{fundamentals.dividend_yield ? `${fundamentals.dividend_yield.toFixed(2)}%` : 'N/A'}</div>
                    </div>
                </div>
            </div>

            {/* Technical Signals */}
            <div style={{
                padding: '1.25rem',
                background: 'var(--bg-glass)',
                borderRadius: 'var(--border-radius)',
                marginBottom: '1rem'
            }}>
                <h4 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Activity size={18} /> Technical Signals
                </h4>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {/* RSI */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.875rem' }}>RSI (14)</span>
                        <span style={{
                            fontWeight: '600',
                            color: signals.rsi?.value < 30 ? 'var(--accent-green)' :
                                signals.rsi?.value > 70 ? 'var(--accent-red)' : 'var(--text-primary)'
                        }}>
                            {signals.rsi?.value?.toFixed(1) || stock.rsi?.toFixed(1)} ({signals.rsi?.signal || (stock.rsi < 30 ? 'Oversold' : stock.rsi > 70 ? 'Overbought' : 'Neutral')})
                        </span>
                    </div>

                    {/* MACD */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.875rem' }}>MACD Signal</span>
                        <span style={{
                            fontWeight: '600',
                            color: stock.macd_signal === 'Bullish' ? 'var(--accent-green)' : 'var(--accent-red)'
                        }}>
                            {stock.macd_signal}
                        </span>
                    </div>

                    {/* Trend */}
                    {signals.moving_averages?.trend && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.875rem' }}>MA Trend</span>
                            <span style={{
                                fontWeight: '600',
                                color: signals.moving_averages.trend.includes('Up') ? 'var(--accent-green)' :
                                    signals.moving_averages.trend.includes('Down') ? 'var(--accent-red)' : 'var(--text-primary)'
                            }}>
                                {signals.moving_averages.trend}
                            </span>
                        </div>
                    )}

                    {/* Volume */}
                    {signals.volume?.signal && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.875rem' }}>Volume</span>
                            <span style={{ fontWeight: '600' }}>
                                {signals.volume.signal} ({signals.volume.ratio?.toFixed(2)}x avg)
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* Returns */}
            <div style={{
                padding: '1.25rem',
                background: 'var(--bg-glass)',
                borderRadius: 'var(--border-radius)'
            }}>
                <h4 style={{ marginBottom: '1rem' }}>Historical Returns</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                    {[
                        { label: '1 Week', value: returns['1w'] },
                        { label: '1 Month', value: returns['1m'] },
                        { label: '3 Months', value: returns['3m'] }
                    ].map(({ label, value }) => (
                        <div key={label} className="metric">
                            <div
                                className="metric-value"
                                style={{ color: value >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}
                            >
                                {value > 0 ? '+' : ''}{value?.toFixed(1)}%
                            </div>
                            <div className="metric-label">{label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Valuation Factors */}
            {stock.valuation?.factors?.length > 0 && (
                <div style={{
                    padding: '1.25rem',
                    background: 'var(--bg-glass)',
                    borderRadius: 'var(--border-radius)',
                    marginTop: '1rem'
                }}>
                    <h4 style={{ marginBottom: '0.75rem' }}>Valuation Factors</h4>
                    <ul style={{
                        listStyle: 'none',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem',
                        fontSize: '0.75rem',
                        color: 'var(--text-secondary)'
                    }}>
                        {stock.valuation.factors.map((factor, i) => (
                            <li key={i}>• {factor}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default StockDetails;
