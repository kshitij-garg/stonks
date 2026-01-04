import { useState, useMemo, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Briefcase, Plus, Trash2, TrendingUp, TrendingDown, PieChart, IndianRupee, Upload, FileUp, X, AlertCircle, CheckCircle, Target, AlertTriangle, BarChart2 } from 'lucide-react';
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import Panel from './Panel';
import DataTable from './DataTable';
import { fetchPortfolioAnalytics } from '../api/stockApi';

const COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#3b82f6', '#84cc16'];

function Portfolio({ data, isLoading, error, onRetry, onStockClick, onAdd, onRemove, onImport, onClear }) {
    const [showAddForm, setShowAddForm] = useState(false);
    const [showImportModal, setShowImportModal] = useState(false);
    const [importStatus, setImportStatus] = useState(null);
    const [formData, setFormData] = useState({ symbol: '', quantity: '', price: '' });
    const [activeView, setActiveView] = useState('overview'); // 'overview' or 'holdings'
    const fileInputRef = useRef(null);

    // Fetch analytics
    const { data: analytics, isLoading: analyticsLoading } = useQuery({
        queryKey: ['portfolio-analytics'],
        queryFn: () => fetchPortfolioAnalytics('weekly'),
        staleTime: 1000 * 60 * 5,
        enabled: (data?.holdings_count || 0) > 0
    });

    const tableColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Stock',
            accessor: row => row.symbol,
            filterable: true,
            render: row => (
                <div>
                    <strong>{row.symbol}</strong>
                    <small className="table-sector">{row.sector}</small>
                </div>
            )
        },
        {
            key: 'quantity',
            label: 'Qty',
            accessor: row => row.quantity,
            sortable: true
        },
        {
            key: 'avg_price',
            label: 'Avg',
            accessor: row => row.avg_price,
            sortable: true,
            render: row => `₹${row.avg_price?.toLocaleString()}`
        },
        {
            key: 'current_price',
            label: 'CMP',
            accessor: row => row.current_price,
            sortable: true,
            render: row => `₹${row.current_price?.toLocaleString()}`
        },
        {
            key: 'pnl_percent',
            label: 'P&L %',
            accessor: row => row.pnl_percent,
            sortable: true,
            render: row => (
                <span className={row.pnl_percent >= 0 ? 'positive' : 'negative'}>
                    {row.pnl_percent >= 0 ? '+' : ''}{row.pnl_percent?.toFixed(2)}%
                </span>
            )
        },
        {
            key: 'upside',
            label: 'Upside',
            accessor: row => row.upside,
            sortable: true,
            render: row => (
                <span className={row.upside >= 0 ? 'positive' : 'negative'}>
                    {row.upside >= 0 ? '+' : ''}{row.upside?.toFixed(1)}%
                </span>
            )
        },
        {
            key: 'predicted_1w',
            label: '1W Pred',
            accessor: row => row.predicted_1w,
            sortable: true,
            render: row => (
                <span className={row.predicted_1w >= 0 ? 'positive' : 'negative'}>
                    {row.predicted_1w >= 0 ? '+' : ''}{row.predicted_1w?.toFixed(2)}%
                </span>
            )
        },
        {
            key: 'recommendation',
            label: 'Action',
            accessor: row => row.recommendation,
            filterable: true,
            render: row => (
                <span className={`action-badge-small ${row.recommendation?.toLowerCase().replace(' ', '-')}`}>
                    {row.recommendation}
                </span>
            )
        },
        {
            key: 'actions',
            label: '',
            sortable: false,
            render: row => (
                <button
                    className="icon-btn remove"
                    onClick={(e) => { e.stopPropagation(); onRemove?.(row.symbol); }}
                >
                    <Trash2 size={14} />
                </button>
            )
        }
    ], [onRemove]);

    const handleAdd = () => {
        if (formData.symbol && formData.quantity > 0 && formData.price > 0) {
            onAdd?.(formData);
            setFormData({ symbol: '', quantity: '', price: '' });
            setShowAddForm(false);
        }
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setImportStatus({ loading: true, message: 'Uploading and parsing file...' });

        try {
            const result = await onImport?.(file);
            if (result?.success) {
                setImportStatus({
                    success: true,
                    message: `Successfully imported ${result.data.added} holdings from ${result.data.broker_detected}`,
                    data: result.data
                });
                setTimeout(() => {
                    setShowImportModal(false);
                    setImportStatus(null);
                }, 2000);
            } else {
                setImportStatus({
                    error: true,
                    message: result?.error || 'Failed to import',
                    details: result?.parse_errors
                });
            }
        } catch (err) {
            setImportStatus({
                error: true,
                message: err.message || 'Import failed'
            });
        }

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const summary = data || {};
    const hasHoldings = summary.holdings_count > 0;

    // Prepare sector data for pie chart
    const sectorData = useMemo(() => {
        if (!analytics?.sector_allocation) return [];
        return Object.entries(analytics.sector_allocation).map(([name, data], i) => ({
            name,
            value: data.percentage,
            amount: data.value,
            color: COLORS[i % COLORS.length]
        }));
    }, [analytics]);

    return (
        <div className="portfolio-container">
            {/* Summary Cards */}
            <div className="portfolio-summary">
                <div className="summary-card glass-card">
                    <div className="summary-icon">
                        <IndianRupee size={24} color="var(--accent-cyan)" />
                    </div>
                    <div className="summary-content">
                        <span className="summary-label">Total Invested</span>
                        <span className="summary-value">₹{(summary.total_invested || 0).toLocaleString()}</span>
                    </div>
                </div>

                <div className="summary-card glass-card">
                    <div className="summary-icon">
                        <PieChart size={24} color="var(--accent-purple)" />
                    </div>
                    <div className="summary-content">
                        <span className="summary-label">Current Value</span>
                        <span className="summary-value">₹{(summary.total_current || 0).toLocaleString()}</span>
                    </div>
                </div>

                <div className={`summary-card glass-card ${summary.total_pnl >= 0 ? 'profit' : 'loss'}`}>
                    <div className="summary-icon">
                        {summary.total_pnl >= 0 ?
                            <TrendingUp size={24} color="var(--accent-green)" /> :
                            <TrendingDown size={24} color="var(--accent-red)" />
                        }
                    </div>
                    <div className="summary-content">
                        <span className="summary-label">Total P&L</span>
                        <span className={`summary-value ${summary.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                            {summary.total_pnl >= 0 ? '+' : ''}₹{(summary.total_pnl || 0).toLocaleString()}
                            <small>({summary.total_pnl_percent >= 0 ? '+' : ''}{(summary.total_pnl_percent || 0).toFixed(2)}%)</small>
                        </span>
                    </div>
                </div>

                {analytics?.predictions && (
                    <div className={`summary-card glass-card prediction ${analytics.predictions.predicted_1w_gain >= 0 ? 'profit' : 'loss'}`}>
                        <div className="summary-icon">
                            <Target size={24} color="#f59e0b" />
                        </div>
                        <div className="summary-content">
                            <span className="summary-label">1-Week Prediction</span>
                            <span className={`summary-value ${analytics.predictions.predicted_1w_gain >= 0 ? 'positive' : 'negative'}`}>
                                {analytics.predictions.predicted_1w_gain >= 0 ? '+' : ''}₹{analytics.predictions.predicted_1w_gain?.toLocaleString()}
                                <small>({analytics.predictions.predicted_1w_gain_percent >= 0 ? '+' : ''}{analytics.predictions.predicted_1w_gain_percent?.toFixed(2)}%)</small>
                            </span>
                        </div>
                    </div>
                )}
            </div>

            {/* Analytics Section */}
            {hasHoldings && analytics && (
                <div className="portfolio-analytics">
                    {/* Sector Allocation */}
                    <div className="analytics-card glass-card">
                        <h3><PieChart size={16} /> Sector Allocation</h3>
                        <div className="sector-chart">
                            <ResponsiveContainer width="100%" height={180}>
                                <RechartsPie>
                                    <Pie
                                        data={sectorData}
                                        dataKey="value"
                                        nameKey="name"
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={40}
                                        outerRadius={70}
                                    >
                                        {sectorData.map((entry, i) => (
                                            <Cell key={i} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(val) => `${val.toFixed(1)}%`} />
                                </RechartsPie>
                            </ResponsiveContainer>
                            <div className="sector-legend">
                                {sectorData.slice(0, 5).map((s, i) => (
                                    <div key={i} className="legend-item">
                                        <span className="legend-dot" style={{ background: s.color }} />
                                        <span>{s.name}</span>
                                        <span>{s.value.toFixed(1)}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Insights */}
                    <div className="analytics-card glass-card insights">
                        <h3><BarChart2 size={16} /> Quick Insights</h3>
                        <div className="insight-row">
                            <span>Stocks to Add More:</span>
                            <div className="insight-symbols positive">
                                {analytics.insights?.stocks_to_buy?.map(s => (
                                    <span key={s} className="symbol-badge buy">{s}</span>
                                ))}
                                {analytics.insights?.stocks_to_buy?.length === 0 && <span className="muted">None</span>}
                            </div>
                        </div>
                        <div className="insight-row">
                            <span>Consider Selling:</span>
                            <div className="insight-symbols negative">
                                {analytics.insights?.stocks_to_sell?.map(s => (
                                    <span key={s} className="symbol-badge sell">{s}</span>
                                ))}
                                {analytics.insights?.stocks_to_sell?.length === 0 && <span className="muted">None</span>}
                            </div>
                        </div>
                        <div className="insight-row">
                            <span>Overbought (RSI>70):</span>
                            <div className="insight-symbols">
                                {analytics.risk?.overbought_stocks?.map(s => (
                                    <span key={s} className="symbol-badge warn">{s}</span>
                                ))}
                                {analytics.risk?.overbought_stocks?.length === 0 && <span className="muted">None</span>}
                            </div>
                        </div>
                        {analytics.risk?.concentration_risk && (
                            <div className="insight-warning">
                                <AlertTriangle size={14} />
                                Concentration Risk: Max holding is {analytics.risk.max_holding_percent}% of portfolio
                            </div>
                        )}
                    </div>

                    {/* Top Upside */}
                    <div className="analytics-card glass-card">
                        <h3><TrendingUp size={16} /> Highest Upside Potential</h3>
                        <div className="upside-list">
                            {analytics.insights?.highest_upside?.slice(0, 4).map((h, i) => (
                                <div key={i} className="upside-item" onClick={() => onStockClick?.(h)}>
                                    <span className="rank">{i + 1}</span>
                                    <span className="symbol">{h.symbol}</span>
                                    <span className={`upside ${h.upside >= 0 ? 'positive' : 'negative'}`}>
                                        {h.upside >= 0 ? '+' : ''}{h.upside?.toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Holdings Table */}
            <Panel
                title="Holdings"
                icon={Briefcase}
                iconColor="#f59e0b"
                isLoading={isLoading || analyticsLoading}
                error={error}
                onRetry={onRetry}
                actions={
                    <div className="portfolio-actions">
                        <button className="import-btn" onClick={() => setShowImportModal(true)}>
                            <Upload size={14} />
                            Import CSV
                        </button>
                        <button className="add-btn" onClick={() => setShowAddForm(!showAddForm)}>
                            <Plus size={14} />
                            Add Holding
                        </button>
                    </div>
                }
            >
                {showAddForm && (
                    <div className="add-form glass-card portfolio-form">
                        <input
                            type="text"
                            placeholder="Symbol"
                            value={formData.symbol}
                            onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                        />
                        <input
                            type="number"
                            placeholder="Quantity"
                            value={formData.quantity}
                            onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                        />
                        <input
                            type="number"
                            placeholder="Avg Price"
                            value={formData.price}
                            onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                        />
                        <button onClick={handleAdd}>Add</button>
                        <button onClick={() => setShowAddForm(false)} className="cancel">Cancel</button>
                    </div>
                )}

                {hasHoldings ? (
                    <DataTable
                        data={analytics?.holdings || summary.holdings || []}
                        columns={tableColumns}
                        onRowClick={onStockClick}
                        pageSize={20}
                        emptyMessage="No holdings"
                    />
                ) : (
                    <div className="empty-state">
                        <Briefcase size={48} color="var(--text-muted)" />
                        <h3>No Holdings Yet</h3>
                        <p>Import your Zerodha/Groww holdings or add manually</p>
                        <button className="import-btn large" onClick={() => setShowImportModal(true)}>
                            <Upload size={18} />
                            Import from Zerodha/Groww
                        </button>
                    </div>
                )}
            </Panel>

            {/* Import Modal */}
            {showImportModal && (
                <>
                    <div className="modal-overlay" onClick={() => !importStatus?.loading && setShowImportModal(false)} />
                    <div className="import-modal glass-card">
                        <div className="modal-header">
                            <h3>
                                <FileUp size={20} />
                                Import Holdings
                            </h3>
                            <button className="close-btn" onClick={() => setShowImportModal(false)}>
                                <X size={16} />
                            </button>
                        </div>

                        <div className="modal-body">
                            {!importStatus && (
                                <>
                                    <p className="import-instructions">
                                        Upload your holdings file from Zerodha, Groww, or other brokers.
                                        <br />
                                        Supported formats: <strong>CSV, Excel (.xlsx)</strong>
                                    </p>

                                    <div className="import-steps">
                                        <div className="step">
                                            <span className="step-num">1</span>
                                            <div>
                                                <strong>Zerodha Kite</strong>
                                                <small>Console → Holdings → Download CSV</small>
                                            </div>
                                        </div>
                                        <div className="step">
                                            <span className="step-num">2</span>
                                            <div>
                                                <strong>Groww</strong>
                                                <small>Stocks → Holdings → Export</small>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="file-upload-zone" onClick={() => fileInputRef.current?.click()}>
                                        <Upload size={32} color="var(--accent-cyan)" />
                                        <p>Click to select file or drag and drop</p>
                                        <small>CSV or Excel file</small>
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept=".csv,.xlsx,.xls"
                                            onChange={handleFileSelect}
                                            style={{ display: 'none' }}
                                        />
                                    </div>
                                </>
                            )}

                            {importStatus?.loading && (
                                <div className="import-loading">
                                    <div className="loading-spinner" />
                                    <p>{importStatus.message}</p>
                                </div>
                            )}

                            {importStatus?.success && (
                                <div className="import-success">
                                    <CheckCircle size={48} color="var(--accent-green)" />
                                    <p>{importStatus.message}</p>
                                </div>
                            )}

                            {importStatus?.error && (
                                <div className="import-error">
                                    <AlertCircle size={48} color="var(--accent-red)" />
                                    <p>{importStatus.message}</p>
                                    {importStatus.details?.length > 0 && (
                                        <ul>
                                            {importStatus.details.map((e, i) => <li key={i}>{e}</li>)}
                                        </ul>
                                    )}
                                    <button onClick={() => setImportStatus(null)}>Try Again</button>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default Portfolio;
