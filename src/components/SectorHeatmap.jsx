import { useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, X } from 'lucide-react';

function SectorHeatmap({ data, isLoading, error, onRetry }) {
    const [selectedSector, setSelectedSector] = useState(null);

    if (isLoading) {
        return (
            <div className="section glass-card">
                <h3 className="section-title">
                    <BarChart3 size={20} color="#8b5cf6" />
                    Sector Performance
                </h3>
                <div className="loading">
                    <div className="loading-spinner" />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="section glass-card">
                <h3 className="section-title">
                    <BarChart3 size={20} color="#8b5cf6" />
                    Sector Performance
                </h3>
                <div className="panel-error">
                    <p>Failed to load sector data</p>
                    {onRetry && <button className="retry-btn" onClick={onRetry}>Retry</button>}
                </div>
            </div>
        );
    }

    if (!data?.length) {
        return (
            <div className="section glass-card">
                <h3 className="section-title">
                    <BarChart3 size={20} color="#8b5cf6" />
                    Sector Performance
                </h3>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No sector data</p>
            </div>
        );
    }

    const getColor = (change) => {
        if (change >= 2) return '#10b981';
        if (change >= 1) return '#34d399';
        if (change >= 0.5) return '#6ee7b7';
        if (change >= 0) return '#4b5563';
        if (change >= -0.5) return '#f87171';
        if (change >= -1) return '#ef4444';
        return '#dc2626';
    };

    const currentSector = data.find(s => s.sector === selectedSector);

    return (
        <div className="section glass-card">
            <h3 className="section-title" style={{ marginBottom: '1rem' }}>
                <BarChart3 size={20} color="#8b5cf6" />
                Sector Performance
                <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Click for details
                </span>
            </h3>

            <div className="heatmap">
                {data.map((sector) => (
                    <div
                        key={sector.sector}
                        className={`heatmap-cell ${selectedSector === sector.sector ? 'selected' : ''}`}
                        style={{ backgroundColor: getColor(sector.change) }}
                        onClick={() => setSelectedSector(selectedSector === sector.sector ? null : sector.sector)}
                    >
                        <div className="sector-name">{sector.sector}</div>
                        <div className="sector-change">
                            {sector.change >= 0 ? '+' : ''}{sector.change?.toFixed(2)}%
                        </div>
                        <div className="sector-count">{sector.stock_count} stocks</div>
                    </div>
                ))}
            </div>

            {/* Modal for Sector Details */}
            {selectedSector && currentSector && (
                <>
                    <div className="sector-modal-overlay" onClick={() => setSelectedSector(null)} />
                    <div className="sector-modal glass-card">
                        <div className="sector-modal-header">
                            <h4>{currentSector.sector}</h4>
                            <button className="close-btn" onClick={() => setSelectedSector(null)}>
                                <X size={16} />
                            </button>
                        </div>

                        <div className="sector-modal-change" style={{ color: getColor(currentSector.change) }}>
                            {currentSector.change >= 0 ? '+' : ''}{currentSector.change?.toFixed(2)}%
                        </div>

                        <div className="sector-performers-row">
                            {/* Top Performer */}
                            {currentSector.top_performer && (
                                <div className="performer-card top">
                                    <div className="performer-header">
                                        <TrendingUp size={14} color="#10b981" />
                                        <span>Best</span>
                                    </div>
                                    <div className="performer-symbol">{currentSector.top_performer.symbol}</div>
                                    <div className="performer-name">{currentSector.top_performer.name}</div>
                                    <div className="performer-change positive">
                                        +{currentSector.top_performer.change?.toFixed(2)}%
                                    </div>
                                </div>
                            )}

                            {/* Worst Performer */}
                            {currentSector.worst_performer && (
                                <div className="performer-card bottom">
                                    <div className="performer-header">
                                        <TrendingDown size={14} color="#ef4444" />
                                        <span>Worst</span>
                                    </div>
                                    <div className="performer-symbol">{currentSector.worst_performer.symbol}</div>
                                    <div className="performer-name">{currentSector.worst_performer.name}</div>
                                    <div className="performer-change negative">
                                        {currentSector.worst_performer.change?.toFixed(2)}%
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* All stocks in sector */}
                        {currentSector.stocks?.length > 0 && (
                            <div className="sector-stocks-list">
                                <div className="sector-stocks-header">All Stocks</div>
                                {currentSector.stocks.map(stock => (
                                    <div key={stock.symbol} className="sector-stock-item">
                                        <span className="stock-sym">{stock.symbol}</span>
                                        <span className="stock-name-small">{stock.name}</span>
                                        <span className={`stock-chg ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                                            {stock.change >= 0 ? '+' : ''}{stock.change?.toFixed(2)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default SectorHeatmap;
