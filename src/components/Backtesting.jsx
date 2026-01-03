import { useState, useMemo } from 'react';
import { LineChart, TrendingUp, TrendingDown, Clock, Target, Award, AlertTriangle, Calendar, BarChart2 } from 'lucide-react';
import Panel from './Panel';
import DataTable from './DataTable';

function Backtesting({ data, stats, isLoading, error, onRetry, onRunBacktest }) {
    const [period, setPeriod] = useState(30);
    const [selectedStrategy, setSelectedStrategy] = useState('all');

    const strategies = [
        { id: 'all', name: 'All Recommendations' },
        { id: 'strong_buy', name: 'Strong Buy Only' },
        { id: 'buy', name: 'Buy & Strong Buy' },
        { id: 'high_score', name: 'Score > 60' },
        { id: 'dcf_undervalued', name: 'DCF Undervalued' }
    ];

    const tableColumns = useMemo(() => [
        {
            key: 'symbol',
            label: 'Symbol',
            accessor: row => row.symbol,
            filterable: true
        },
        {
            key: 'action',
            label: 'Recommendation',
            accessor: row => row.action,
            filterable: true,
            render: row => (
                <span className={`action-badge-small ${row.action?.toLowerCase().replace(' ', '-')}`}>
                    {row.action}
                </span>
            )
        },
        {
            key: 'start_price',
            label: 'Entry Price',
            accessor: row => row.start_price,
            sortable: true,
            render: row => `₹${row.start_price?.toLocaleString()}`
        },
        {
            key: 'end_price',
            label: 'Current Price',
            accessor: row => row.end_price,
            sortable: true,
            render: row => `₹${row.end_price?.toLocaleString()}`
        },
        {
            key: 'return',
            label: 'Return',
            accessor: row => row.return,
            sortable: true,
            render: row => (
                <span className={row.return >= 0 ? 'positive' : 'negative'}>
                    {row.return >= 0 ? '+' : ''}{row.return?.toFixed(2)}%
                </span>
            )
        }
    ], []);

    // Handle no data state
    if (!data || data.no_data) {
        return (
            <div className="backtest-container">
                <Panel title="Backtesting Engine" icon={LineChart} iconColor="#8b5cf6">
                    <div className="backtest-no-data">
                        <Clock size={48} color="var(--text-muted)" />
                        <h3>Building Recommendation History</h3>
                        <p>
                            The backtesting engine tracks your recommendations over time to measure performance.
                            <br />
                            Data collection has started. Check back in a few days for results.
                        </p>

                        {stats && (
                            <div className="tracking-stats">
                                <div className="stat-item">
                                    <span className="stat-value">{stats.total_recommendations || 0}</span>
                                    <span className="stat-label">Recommendations Tracked</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-value">{stats.tracking_days || 0}</span>
                                    <span className="stat-label">Days of Data</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-value">{stats.latest_date || 'N/A'}</span>
                                    <span className="stat-label">Latest Snapshot</span>
                                </div>
                            </div>
                        )}

                        <div className="backtest-info glass-card">
                            <h4>How It Works</h4>
                            <ul>
                                <li>Every day, your current recommendations are saved with prices</li>
                                <li>After 7, 14, 30 days, we compare the prices to measure accuracy</li>
                                <li>You'll see which recommendation types (Strong Buy, Buy, etc.) performed best</li>
                                <li>Track win rate, average return, best/worst picks over time</li>
                            </ul>
                        </div>
                    </div>
                </Panel>
            </div>
        );
    }

    const {
        period_days,
        start_date,
        end_date,
        by_action = {},
        total_recommendations = 0,
        profitable_count = 0,
        avg_return = 0,
        win_rate = 0,
        best_pick,
        worst_pick,
        detail = []
    } = data;

    return (
        <div className="backtest-container">
            {/* Controls */}
            <div className="backtest-controls glass-card">
                <div className="control-group">
                    <label>Backtest Period</label>
                    <div className="period-buttons">
                        {[7, 14, 30, 60, 90].map(days => (
                            <button
                                key={days}
                                className={period === days ? 'active' : ''}
                                onClick={() => { setPeriod(days); onRunBacktest?.(days); }}
                            >
                                {days}D
                            </button>
                        ))}
                    </div>
                </div>

                <div className="control-group">
                    <label>Strategy</label>
                    <select value={selectedStrategy} onChange={e => setSelectedStrategy(e.target.value)}>
                        {strategies.map(s => (
                            <option key={s.id} value={s.id}>{s.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="backtest-summary">
                <div className="backtest-stat">
                    <div className="backtest-stat-value" style={{ color: avg_return >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                        {avg_return >= 0 ? '+' : ''}{avg_return?.toFixed(2)}%
                    </div>
                    <div className="backtest-stat-label">Avg Return</div>
                </div>

                <div className="backtest-stat">
                    <div className="backtest-stat-value" style={{ color: win_rate >= 50 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                        {win_rate?.toFixed(1)}%
                    </div>
                    <div className="backtest-stat-label">Win Rate</div>
                </div>

                <div className="backtest-stat">
                    <div className="backtest-stat-value">{profitable_count}/{total_recommendations}</div>
                    <div className="backtest-stat-label">Profitable Trades</div>
                </div>

                <div className="backtest-stat">
                    <div className="backtest-stat-value">{period_days} days</div>
                    <div className="backtest-stat-label">Period</div>
                </div>
            </div>

            {/* Best and Worst Picks */}
            <div className="backtest-highlights">
                {best_pick && (
                    <div className="highlight-card best glass-card">
                        <div className="highlight-header">
                            <Award size={20} color="#10b981" />
                            <span>Best Pick</span>
                        </div>
                        <div className="highlight-symbol">{best_pick.symbol}</div>
                        <div className="highlight-return positive">+{best_pick.return?.toFixed(2)}%</div>
                    </div>
                )}

                {worst_pick && (
                    <div className="highlight-card worst glass-card">
                        <div className="highlight-header">
                            <AlertTriangle size={20} color="#ef4444" />
                            <span>Worst Pick</span>
                        </div>
                        <div className="highlight-symbol">{worst_pick.symbol}</div>
                        <div className="highlight-return negative">{worst_pick.return?.toFixed(2)}%</div>
                    </div>
                )}
            </div>

            {/* Performance by Action Type */}
            <Panel title="Performance by Recommendation Type" icon={BarChart2} iconColor="#f59e0b">
                <div className="action-performance-grid">
                    {Object.entries(by_action).map(([action, stats]) => (
                        <div key={action} className="action-performance-card">
                            <div className="action-name">{action}</div>
                            <div className="action-stats">
                                <div className="action-stat">
                                    <span className={stats.avg_return >= 0 ? 'positive' : 'negative'}>
                                        {stats.avg_return >= 0 ? '+' : ''}{stats.avg_return?.toFixed(2)}%
                                    </span>
                                    <label>Avg Return</label>
                                </div>
                                <div className="action-stat">
                                    <span>{stats.count}</span>
                                    <label>Count</label>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </Panel>

            {/* Detailed Results Table */}
            <Panel title="Detailed Results" icon={Target} iconColor="#06b6d4">
                <DataTable
                    data={detail}
                    columns={tableColumns}
                    pageSize={15}
                    emptyMessage="No backtest results available"
                />
            </Panel>

            {/* Period Info */}
            <div className="backtest-footer">
                <Calendar size={14} />
                <span>Period: {start_date} to {end_date}</span>
            </div>
        </div>
    );
}

export default Backtesting;
