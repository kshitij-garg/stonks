import { useState, useMemo } from 'react';
import { Bell, Plus, Trash2, TrendingUp, TrendingDown, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import Panel from './Panel';
import DataTable from './DataTable';

function Alerts({ alerts, history, isLoading, error, onRetry, onCreate, onDelete }) {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({
        symbol: '',
        targetPrice: '',
        condition: 'above',
        notes: ''
    });

    const alertColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Symbol',
            accessor: row => row.symbol,
            render: row => <strong>{row.symbol}</strong>
        },
        {
            key: 'condition',
            label: 'Trigger',
            accessor: row => row.condition,
            render: row => (
                <span className={`condition-badge ${row.condition}`}>
                    {row.condition === 'above' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {row.condition}
                </span>
            )
        },
        {
            key: 'target_price',
            label: 'Target',
            accessor: row => row.target_price,
            sortable: true,
            render: row => `₹${row.target_price?.toLocaleString()}`
        },
        {
            key: 'created_at',
            label: 'Created',
            accessor: row => row.created_at,
            sortable: true,
            render: row => new Date(row.created_at).toLocaleDateString()
        },
        {
            key: 'notes',
            label: 'Notes',
            accessor: row => row.notes || '-'
        },
        {
            key: 'actions',
            label: '',
            render: row => (
                <button
                    className="icon-btn remove"
                    onClick={() => onDelete?.(row.id)}
                >
                    <Trash2 size={14} />
                </button>
            )
        }
    ], [onDelete]);

    const historyColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Symbol',
            accessor: row => row.symbol,
            render: row => <strong>{row.symbol}</strong>
        },
        {
            key: 'condition',
            label: 'Condition',
            accessor: row => row.condition
        },
        {
            key: 'target_price',
            label: 'Target',
            accessor: row => row.target_price,
            render: row => `₹${row.target_price?.toLocaleString()}`
        },
        {
            key: 'triggered_price',
            label: 'Triggered At',
            accessor: row => row.triggered_price,
            render: row => `₹${row.triggered_price?.toLocaleString()}`
        },
        {
            key: 'triggered_at',
            label: 'Date',
            accessor: row => row.triggered_at,
            render: row => new Date(row.triggered_at).toLocaleString()
        }
    ], []);

    const handleCreate = () => {
        if (formData.symbol && formData.targetPrice > 0) {
            onCreate?.(formData);
            setFormData({ symbol: '', targetPrice: '', condition: 'above', notes: '' });
            setShowCreateForm(false);
        }
    };

    return (
        <div className="alerts-container">
            <Panel
                title="Price Alerts"
                icon={Bell}
                iconColor="#f59e0b"
                isLoading={isLoading}
                error={error}
                onRetry={onRetry}
                actions={
                    <button className="add-btn" onClick={() => setShowCreateForm(!showCreateForm)}>
                        <Plus size={14} />
                        New Alert
                    </button>
                }
            >
                {showCreateForm && (
                    <div className="alert-form glass-card">
                        <div className="form-row">
                            <input
                                type="text"
                                placeholder="Symbol (e.g., RELIANCE)"
                                value={formData.symbol}
                                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                            />
                            <input
                                type="number"
                                placeholder="Target Price"
                                value={formData.targetPrice}
                                onChange={(e) => setFormData({ ...formData, targetPrice: parseFloat(e.target.value) })}
                            />
                            <select
                                value={formData.condition}
                                onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                            >
                                <option value="above">Above</option>
                                <option value="below">Below</option>
                            </select>
                        </div>
                        <div className="form-row">
                            <input
                                type="text"
                                placeholder="Notes (optional)"
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                className="notes-input"
                            />
                            <button onClick={handleCreate}>Create</button>
                            <button onClick={() => setShowCreateForm(false)} className="cancel">Cancel</button>
                        </div>
                    </div>
                )}

                {alerts?.length > 0 ? (
                    <DataTable
                        data={alerts}
                        columns={alertColumns}
                        pageSize={10}
                        emptyMessage="No active alerts"
                    />
                ) : (
                    <div className="empty-state">
                        <Bell size={48} color="var(--text-muted)" />
                        <h3>No Active Alerts</h3>
                        <p>Create price alerts to get notified when stocks hit your target</p>
                    </div>
                )}
            </Panel>

            {history?.length > 0 && (
                <Panel
                    title="Alert History"
                    icon={Clock}
                    iconColor="#8b5cf6"
                >
                    <DataTable
                        data={history}
                        columns={historyColumns}
                        pageSize={10}
                    />
                </Panel>
            )}
        </div>
    );
}

export default Alerts;
