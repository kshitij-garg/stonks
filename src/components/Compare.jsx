import { useState } from 'react';
import { GitCompare, Plus, X } from 'lucide-react';
import Panel from './Panel';

function Compare({ data, isLoading, error, onAdd, onRemove }) {
    const [searchSymbol, setSearchSymbol] = useState('');

    const handleAdd = () => {
        if (searchSymbol.trim()) {
            onAdd?.(searchSymbol.trim().toUpperCase());
            setSearchSymbol('');
        }
    };

    const formatMarketCap = (value) => {
        if (!value) return '-';
        if (value >= 1e12) return `₹${(value / 1e12).toFixed(1)}T`;
        if (value >= 1e9) return `₹${(value / 1e9).toFixed(0)}B`;
        if (value >= 1e7) return `₹${(value / 1e7).toFixed(0)}Cr`;
        return `₹${value.toLocaleString()}`;
    };

    // Helper to safely extract values from nested objects
    const getValue = (stock, key) => {
        switch (key) {
            case 'price':
                return stock.price;
            case 'change_percent':
                return stock.change_percent;
            case 'score':
                return stock.scores?.composite ?? stock.score;
            case 'rsi':
                return stock.rsi;
            case 'pe_ratio':
                return stock.fundamentals?.pe_ratio ?? stock.pe_ratio;
            case 'market_cap':
                return stock.market_cap ?? stock.fundamentals?.market_cap;
            case 'upside':
                return stock.recommendation?.upside ?? stock.upside;
            case 'dcf_margin':
                return stock.dcf?.margin_of_safety ?? stock.dcf_margin;
            case 'macd_signal':
                return stock.macd_signal;
            case 'valuation':
                return stock.valuation?.status ?? stock.valuation;
            case 'action':
                return stock.recommendation?.action ?? 'N/A';
            default:
                return stock[key];
        }
    };

    const metrics = [
        { key: 'price', label: 'Price', format: v => typeof v === 'number' ? `₹${v.toLocaleString()}` : '-' },
        { key: 'change_percent', label: 'Change', format: v => typeof v === 'number' ? `${v >= 0 ? '+' : ''}${v.toFixed(2)}%` : '-', color: true },
        { key: 'score', label: 'Score', format: v => typeof v === 'number' ? v.toFixed(0) : '-' },
        { key: 'rsi', label: 'RSI', format: v => typeof v === 'number' ? v.toFixed(0) : '-' },
        { key: 'pe_ratio', label: 'P/E', format: v => typeof v === 'number' ? v.toFixed(1) : '-' },
        { key: 'market_cap', label: 'Market Cap', format: v => formatMarketCap(v) },
        { key: 'upside', label: 'Upside', format: v => typeof v === 'number' ? `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` : '-', color: true },
        { key: 'dcf_margin', label: 'DCF Margin', format: v => typeof v === 'number' ? `${v >= 0 ? '+' : ''}${v.toFixed(0)}%` : '-', color: true },
        { key: 'macd_signal', label: 'MACD', format: v => typeof v === 'string' ? v : '-' },
        { key: 'valuation', label: 'Valuation', format: v => typeof v === 'string' ? v : '-' },
        { key: 'action', label: 'Action', format: v => typeof v === 'string' ? v : '-' },
    ];

    const stocks = data || [];

    return (
        <div className="compare-container">
            <Panel
                title="Stock Comparison"
                icon={GitCompare}
                iconColor="#8b5cf6"
                isLoading={isLoading && stocks.length === 0}
                error={error}
            >
                {/* Add Stock */}
                <div className="compare-add-bar">
                    <input
                        type="text"
                        placeholder="Add stock symbol to compare..."
                        value={searchSymbol}
                        onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
                        onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
                    />
                    <button onClick={handleAdd} disabled={!searchSymbol.trim() || stocks.length >= 5}>
                        <Plus size={14} />
                        Add
                    </button>
                    <span className="compare-count">{stocks.length}/5 stocks</span>
                </div>

                {stocks.length > 0 ? (
                    <div className="compare-table-container">
                        <table className="compare-table">
                            <thead>
                                <tr>
                                    <th className="metric-label">Metric</th>
                                    {stocks.map(stock => (
                                        <th key={stock.symbol} className="stock-header">
                                            <div className="stock-header-content">
                                                <span>{stock.symbol}</span>
                                                <button
                                                    className="remove-stock"
                                                    onClick={() => onRemove?.(stock.symbol)}
                                                >
                                                    <X size={12} />
                                                </button>
                                            </div>
                                            <small>{stock.name}</small>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {metrics.map(metric => (
                                    <tr key={metric.key}>
                                        <td className="metric-label">{metric.label}</td>
                                        {stocks.map(stock => {
                                            const value = getValue(stock, metric.key);
                                            const formatted = metric.format(value);
                                            const colorClass = metric.color && typeof value === 'number' ? (value >= 0 ? 'positive' : 'negative') : '';

                                            return (
                                                <td key={`${stock.symbol}-${metric.key}`} className={colorClass}>
                                                    {formatted}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <GitCompare size={48} color="var(--text-muted)" />
                        <h3>Compare Up to 5 Stocks</h3>
                        <p>Add stock symbols above to compare metrics side by side</p>
                    </div>
                )}
            </Panel>
        </div>
    );
}

export default Compare;
