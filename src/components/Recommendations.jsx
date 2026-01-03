import { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Target, CheckCircle, XCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import Panel from './Panel';
import DataTable from './DataTable';

function Recommendations({ data, isLoading, error, onStockClick, timeframe, onRetry }) {
    const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'table'

    const tableColumns = useMemo(() => [
        {
            key: 'rank',
            label: '#',
            accessor: row => row.rank,
            width: '50px',
            sortable: true
        },
        {
            key: 'symbol',
            label: 'Symbol',
            accessor: row => row.symbol,
            filterable: true,
            render: row => (
                <div>
                    <strong>{row.symbol}</strong>
                    <span className="table-sector">{row.sector}</span>
                </div>
            )
        },
        {
            key: 'price',
            label: 'Price',
            accessor: row => row.price,
            sortable: true,
            render: row => `₹${row.price?.toLocaleString()}`
        },
        {
            key: 'change',
            label: 'Change',
            accessor: row => row.change_percent,
            sortable: true,
            render: row => (
                <span className={row.change_percent >= 0 ? 'positive' : 'negative'}>
                    {row.change_percent >= 0 ? '+' : ''}{row.change_percent?.toFixed(2)}%
                </span>
            )
        },
        {
            key: 'score',
            label: 'Score',
            accessor: row => row.scores?.composite,
            sortable: true,
            render: row => (
                <span className={`score-badge ${row.scores?.composite >= 60 ? 'high' : row.scores?.composite >= 40 ? 'medium' : 'low'}`}>
                    {row.scores?.composite?.toFixed(0)}
                </span>
            )
        },
        {
            key: 'rsi',
            label: 'RSI',
            accessor: row => row.rsi,
            sortable: true
        },
        {
            key: 'macd',
            label: 'MACD',
            accessor: row => row.macd_signal,
            filterable: true,
            render: row => (
                <span className={`macd-badge ${row.macd_signal === 'Bullish' ? 'bullish' : 'bearish'}`}>
                    {row.macd_signal}
                </span>
            )
        },
        {
            key: 'action',
            label: 'Action',
            accessor: row => row.recommendation?.action,
            filterable: true,
            render: row => (
                <span
                    className="action-badge-small"
                    style={{ background: row.recommendation?.color }}
                >
                    {row.recommendation?.action}
                </span>
            )
        },
        {
            key: 'dcf',
            label: 'DCF Margin',
            accessor: row => row.dcf?.margin_of_safety,
            sortable: true,
            render: row => (
                <span className={row.dcf?.margin_of_safety > 0 ? 'positive' : 'negative'}>
                    {row.dcf?.margin_of_safety > 0 ? '+' : ''}{row.dcf?.margin_of_safety?.toFixed(0)}%
                </span>
            )
        },
        {
            key: 'upside',
            label: 'Upside',
            accessor: row => row.recommendation?.upside,
            sortable: true,
            render: row => (
                <span className={row.recommendation?.upside > 0 ? 'positive' : 'negative'}>
                    {row.recommendation?.upside?.toFixed(1)}%
                </span>
            )
        },
        {
            key: 'sector',
            label: 'Sector',
            accessor: row => row.sector,
            filterable: true
        }
    ], []);

    if (isLoading || error || !data) {
        return (
            <Panel
                title="Market Recommendations"
                icon={Target}
                iconColor="#06b6d4"
                isLoading={isLoading}
                error={error}
                onRetry={onRetry}
            />
        );
    }

    const { summary, top_picks, avoid_list, all_recommendations } = data;

    const getActionColor = (action) => {
        switch (action) {
            case 'STRONG BUY': return '#10b981';
            case 'BUY': return '#34d399';
            case 'HOLD': return '#f59e0b';
            case 'SELL': return '#f87171';
            case 'STRONG SELL': return '#ef4444';
            default: return '#6b7280';
        }
    };

    return (
        <div className="recommendations-container">
            {/* Summary Cards */}
            <div className="rec-summary glass-card">
                <div className="rec-summary-header">
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Target size={24} color="#06b6d4" />
                        Market Recommendations
                    </h2>
                    <div className="view-toggle">
                        <button
                            className={viewMode === 'cards' ? 'active' : ''}
                            onClick={() => setViewMode('cards')}
                        >
                            Cards
                        </button>
                        <button
                            className={viewMode === 'table' ? 'active' : ''}
                            onClick={() => setViewMode('table')}
                        >
                            Table
                        </button>
                    </div>
                </div>

                <div className="summary-grid">
                    <div className="summary-item strong-buy">
                        <div className="summary-value">{summary?.strong_buy || 0}</div>
                        <div className="summary-label">Strong Buy</div>
                    </div>
                    <div className="summary-item buy">
                        <div className="summary-value">{summary?.buy || 0}</div>
                        <div className="summary-label">Buy</div>
                    </div>
                    <div className="summary-item hold">
                        <div className="summary-value">{summary?.hold || 0}</div>
                        <div className="summary-label">Hold</div>
                    </div>
                    <div className="summary-item sell">
                        <div className="summary-value">{summary?.sell || 0}</div>
                        <div className="summary-label">Sell</div>
                    </div>
                    <div className="summary-item strong-sell">
                        <div className="summary-value">{summary?.strong_sell || 0}</div>
                        <div className="summary-label">Strong Sell</div>
                    </div>
                </div>
            </div>

            {viewMode === 'cards' ? (
                <>
                    {/* Top Picks and Avoid List Side by Side */}
                    <div className="rec-columns">
                        <Panel title="Top 5 Picks" icon={CheckCircle} iconColor="#10b981">
                            <div className="rec-list">
                                {top_picks?.map((stock, i) => (
                                    <div
                                        key={stock.symbol}
                                        className="rec-card buy-card"
                                        onClick={() => onStockClick(stock)}
                                    >
                                        <div className="rec-rank">{i + 1}</div>
                                        <div className="rec-info">
                                            <h4>{stock.symbol}</h4>
                                            <p>{stock.name}</p>
                                            <div className="rec-sector">{stock.sector}</div>
                                        </div>
                                        <div className="rec-metrics">
                                            <div className="rec-price">₹{stock.price?.toLocaleString()}</div>
                                            <div className={`rec-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                                {stock.change_percent >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                                {stock.change_percent?.toFixed(2)}%
                                            </div>
                                        </div>
                                        <div className="rec-action">
                                            <div
                                                className="action-badge"
                                                style={{ background: getActionColor(stock.recommendation?.action) }}
                                            >
                                                {stock.recommendation?.action}
                                            </div>
                                            <div className="confidence">
                                                {stock.recommendation?.confidence?.toFixed(0)}% conf
                                            </div>
                                        </div>
                                        <div className="rec-dcf">
                                            <span>DCF</span>
                                            <strong className={stock.dcf?.margin_of_safety > 0 ? 'positive' : 'negative'}>
                                                {stock.dcf?.margin_of_safety > 0 ? '+' : ''}{stock.dcf?.margin_of_safety?.toFixed(0)}%
                                            </strong>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Panel>

                        <Panel title="Stocks to Avoid" icon={XCircle} iconColor="#ef4444">
                            <div className="rec-list">
                                {avoid_list?.map((stock, i) => (
                                    <div
                                        key={stock.symbol}
                                        className="rec-card sell-card"
                                        onClick={() => onStockClick(stock)}
                                    >
                                        <div className="rec-rank">{i + 1}</div>
                                        <div className="rec-info">
                                            <h4>{stock.symbol}</h4>
                                            <p>{stock.name}</p>
                                            <div className="rec-sector">{stock.sector}</div>
                                        </div>
                                        <div className="rec-metrics">
                                            <div className="rec-price">₹{stock.price?.toLocaleString()}</div>
                                            <div className={`rec-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                                {stock.change_percent >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                                                {stock.change_percent?.toFixed(2)}%
                                            </div>
                                        </div>
                                        <div className="rec-action">
                                            <div
                                                className="action-badge"
                                                style={{ background: getActionColor(stock.recommendation?.action) }}
                                            >
                                                {stock.recommendation?.action}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Panel>
                    </div>
                </>
            ) : (
                /* Table View */
                <div className="rec-table-section glass-card">
                    <DataTable
                        data={all_recommendations || []}
                        columns={tableColumns}
                        onRowClick={onStockClick}
                        pageSize={15}
                        emptyMessage="No recommendations available"
                    />
                </div>
            )}
        </div>
    );
}

export default Recommendations;
