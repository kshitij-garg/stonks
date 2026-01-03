import { useState, useMemo } from 'react';
import { Eye, Plus, Trash2, TrendingUp, TrendingDown, Star, Bell } from 'lucide-react';
import Panel from './Panel';
import DataTable from './DataTable';

function Watchlist({ data, isLoading, error, onRetry, onStockClick, onAdd, onRemove }) {
    const [addSymbol, setAddSymbol] = useState('');
    const [showAddForm, setShowAddForm] = useState(false);

    const tableColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Symbol',
            accessor: row => row.symbol,
            render: row => (
                <div className="stock-cell">
                    <Star size={12} color="#f59e0b" fill="#f59e0b" />
                    <strong>{row.symbol}</strong>
                </div>
            )
        },
        {
            key: 'added_at',
            label: 'Added',
            accessor: row => row.added_at,
            sortable: true,
            render: row => new Date(row.added_at).toLocaleDateString()
        },
        {
            key: 'added_price',
            label: 'Entry Price',
            accessor: row => row.added_price,
            sortable: true,
            render: row => row.added_price ? `₹${row.added_price.toLocaleString()}` : '-'
        },
        {
            key: 'current_price',
            label: 'Current',
            accessor: row => row.current_price,
            sortable: true,
            render: row => row.current_price ? `₹${row.current_price.toLocaleString()}` : '-'
        },
        {
            key: 'change',
            label: 'Change',
            accessor: row => row.change_percent,
            sortable: true,
            render: row => (
                <span className={row.change_percent >= 0 ? 'positive' : 'negative'}>
                    {row.change_percent >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {row.change_percent >= 0 ? '+' : ''}{row.change_percent?.toFixed(2)}%
                </span>
            )
        },
        {
            key: 'actions',
            label: '',
            sortable: false,
            render: row => (
                <div className="action-buttons">
                    <button className="icon-btn alert" title="Set Alert">
                        <Bell size={14} />
                    </button>
                    <button className="icon-btn remove" onClick={(e) => { e.stopPropagation(); onRemove?.(row.symbol); }}>
                        <Trash2 size={14} />
                    </button>
                </div>
            )
        }
    ], [onRemove]);

    const handleAdd = () => {
        if (addSymbol.trim()) {
            onAdd?.(addSymbol.trim().toUpperCase());
            setAddSymbol('');
            setShowAddForm(false);
        }
    };

    return (
        <div className="watchlist-container">
            <Panel
                title="My Watchlist"
                icon={Eye}
                iconColor="#f59e0b"
                isLoading={isLoading}
                error={error}
                onRetry={onRetry}
                actions={
                    <button className="add-btn" onClick={() => setShowAddForm(!showAddForm)}>
                        <Plus size={14} />
                        Add Stock
                    </button>
                }
            >
                {showAddForm && (
                    <div className="add-form glass-card">
                        <input
                            type="text"
                            placeholder="Enter symbol (e.g., RELIANCE)"
                            value={addSymbol}
                            onChange={(e) => setAddSymbol(e.target.value.toUpperCase())}
                            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
                        />
                        <button onClick={handleAdd} disabled={!addSymbol.trim()}>Add</button>
                        <button onClick={() => setShowAddForm(false)} className="cancel">Cancel</button>
                    </div>
                )}

                {data?.stocks?.length > 0 ? (
                    <DataTable
                        data={data.stocks}
                        columns={tableColumns}
                        onRowClick={onStockClick}
                        pageSize={15}
                        emptyMessage="No stocks in watchlist"
                    />
                ) : (
                    <div className="empty-state">
                        <Eye size={48} color="var(--text-muted)" />
                        <h3>Your Watchlist is Empty</h3>
                        <p>Click "Add Stock" to start tracking your favorite stocks</p>
                    </div>
                )}
            </Panel>
        </div>
    );
}

export default Watchlist;
