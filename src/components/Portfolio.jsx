import { useState, useMemo, useRef } from 'react';
import { Briefcase, Plus, Trash2, TrendingUp, TrendingDown, PieChart, IndianRupee, Upload, FileUp, X, AlertCircle, CheckCircle } from 'lucide-react';
import Panel from './Panel';
import DataTable from './DataTable';

function Portfolio({ data, isLoading, error, onRetry, onStockClick, onAdd, onRemove, onImport, onClear }) {
    const [showAddForm, setShowAddForm] = useState(false);
    const [showImportModal, setShowImportModal] = useState(false);
    const [importStatus, setImportStatus] = useState(null);
    const [formData, setFormData] = useState({ symbol: '', quantity: '', price: '' });
    const fileInputRef = useRef(null);

    const tableColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Stock',
            accessor: row => row.symbol,
            filterable: true,
            render: row => <strong>{row.symbol}</strong>
        },
        {
            key: 'quantity',
            label: 'Qty',
            accessor: row => row.quantity,
            sortable: true
        },
        {
            key: 'avg_price',
            label: 'Avg Price',
            accessor: row => row.avg_price,
            sortable: true,
            render: row => `₹${row.avg_price?.toLocaleString()}`
        },
        {
            key: 'current_price',
            label: 'Current',
            accessor: row => row.current_price,
            sortable: true,
            render: row => `₹${row.current_price?.toLocaleString()}`
        },
        {
            key: 'invested_value',
            label: 'Invested',
            accessor: row => row.invested_value,
            sortable: true,
            render: row => `₹${row.invested_value?.toLocaleString()}`
        },
        {
            key: 'current_value',
            label: 'Current Value',
            accessor: row => row.current_value,
            sortable: true,
            render: row => `₹${row.current_value?.toLocaleString()}`
        },
        {
            key: 'pnl',
            label: 'P&L',
            accessor: row => row.pnl,
            sortable: true,
            render: row => (
                <div className="pnl-cell">
                    <span className={row.pnl >= 0 ? 'positive' : 'negative'}>
                        {row.pnl >= 0 ? '+' : ''}₹{row.pnl?.toLocaleString()}
                    </span>
                    <small className={row.pnl_percent >= 0 ? 'positive' : 'negative'}>
                        ({row.pnl_percent >= 0 ? '+' : ''}{row.pnl_percent?.toFixed(2)}%)
                    </small>
                </div>
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

        // Reset file input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const summary = data || {};
    const hasHoldings = summary.holdings_count > 0;

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

                <div className="summary-card glass-card">
                    <div className="summary-icon">
                        <Briefcase size={24} color="var(--accent-orange)" />
                    </div>
                    <div className="summary-content">
                        <span className="summary-label">Holdings</span>
                        <span className="summary-value">{summary.holdings_count || 0} stocks</span>
                    </div>
                </div>
            </div>

            {/* Holdings Table */}
            <Panel
                title="Holdings"
                icon={Briefcase}
                iconColor="#f59e0b"
                isLoading={isLoading}
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
                       