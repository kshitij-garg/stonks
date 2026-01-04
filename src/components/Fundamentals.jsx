import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { FileText, TrendingUp, TrendingDown, DollarSign, PieChart, Users, ChevronDown, ChevronUp } from 'lucide-react';
import Panel from './Panel';

function Fundamentals({ data, isLoading, error, onRetry, symbol }) {
    const [activeSection, setActiveSection] = useState('quarterly');

    if (isLoading) {
        return (
            <div className="fundamentals-container">
                <Panel title="Fundamentals" icon={FileText} iconColor="#8b5cf6" isLoading />
            </div>
        );
    }

    if (error) {
        return (
            <div className="fundamentals-container">
                <Panel title="Fundamentals" icon={FileText} iconColor="#8b5cf6" error={error} onRetry={onRetry} />
            </div>
        );
    }

    const quarterly = data?.quarterly_results;
    const balanceSheet = data?.balance_sheet;
    const cashFlow = data?.cash_flow;
    const peers = data?.peer_comparison;

    const formatCurrency = (val) => {
        if (!val) return '-';
        const absVal = Math.abs(val);
        if (absVal >= 1e12) return `₹${(val / 1e12).toFixed(1)}T`;
        if (absVal >= 1e9) return `₹${(val / 1e9).toFixed(1)}B`;
        if (absVal >= 1e7) return `₹${(val / 1e7).toFixed(0)}Cr`;
        if (absVal >= 1e5) return `₹${(val / 1e5).toFixed(0)}L`;
        return `₹${val.toLocaleString()}`;
    };

    const sections = [
        { id: 'quarterly', label: 'Quarterly Results', icon: BarChart },
        { id: 'balance', label: 'Balance Sheet', icon: PieChart },
        { id: 'peers', label: 'Peer Comparison', icon: Users },
    ];

    return (
        <div className="fundamentals-container">
            <div className="fundamentals-nav">
                {sections.map(section => (
                    <button
                        key={section.id}
                        className={`fund-nav-btn ${activeSection === section.id ? 'active' : ''}`}
                        onClick={() => setActiveSection(section.id)}
                    >
                        <section.icon size={14} />
                        {section.label}
                    </button>
                ))}
            </div>

            {activeSection === 'quarterly' && quarterly?.quarters && (
                <Panel title="Quarterly Results" icon={FileText} iconColor="#8b5cf6">
                    <div className="quarterly-summary">
                        {quarterly.latest && (
                            <div className="summary-row">
                                <div className="summary-metric">
                                    <span className="label">Revenue</span>
                                    <span className="value">{formatCurrency(quarterly.latest.revenue)}</span>
                                    {quarterly.latest.revenue_yoy && (
                                        <span className={`change ${quarterly.latest.revenue_yoy >= 0 ? 'positive' : 'negative'}`}>
                                            YoY: {quarterly.latest.revenue_yoy >= 0 ? '+' : ''}{quarterly.latest.revenue_yoy.toFixed(1)}%
                                        </span>
                                    )}
                                </div>
                                <div className="summary-metric">
                                    <span className="label">Net Income</span>
                                    <span className="value">{formatCurrency(quarterly.latest.net_income)}</span>
                                </div>
                                <div className="summary-metric">
                                    <span className="label">Operating Margin</span>
                                    <span className="value">{quarterly.latest.operating_margin?.toFixed(1)}%</span>
                                </div>
                                <div className="summary-metric">
                                    <span className="label">Net Margin</span>
                                    <span className="value">{quarterly.latest.net_margin?.toFixed(1)}%</span>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="quarterly-chart">
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={quarterly.quarters.slice(0, 4).reverse()}>
                                <XAxis dataKey="quarter" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                                <YAxis tickFormatter={(v) => formatCurrency(v)} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                                <Tooltip
                                    formatter={(v) => formatCurrency(v)}
                                    contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}
                                />
                                <Bar dataKey="revenue" fill="var(--accent-cyan)" name="Revenue" />
                                <Bar dataKey="net_income" fill="var(--accent-green)" name="Net Income" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <table className="fundamentals-table">
                        <thead>
                            <tr>
                                <th>Quarter</th>
                                <th>Revenue</th>
                                <th>Net Income</th>
                                <th>Op. Margin</th>
                                <th>Net Margin</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quarterly.quarters.slice(0, 6).map((q, i) => (
                                <tr key={i}>
                                    <td>{q.quarter}</td>
                                    <td>{formatCurrency(q.revenue)}</td>
                                    <td className={q.net_income >= 0 ? 'positive' : 'negative'}>{formatCurrency(q.net_income)}</td>
                                    <td>{q.operating_margin?.toFixed(1)}%</td>
                                    <td>{q.net_margin?.toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Panel>
            )}

            {activeSection === 'balance' && balanceSheet && !balanceSheet.error && (
                <Panel title="Balance Sheet" icon={PieChart} iconColor="#f59e0b">
                    <div className="balance-sheet-grid">
                        <div className="bs-section">
                            <h4>Assets</h4>
                            <div className="bs-row">
                                <span>Total Assets</span>
                                <span>{formatCurrency(balanceSheet.current?.total_assets)}</span>
                            </div>
                            <div className="bs-row">
                                <span>Current Assets</span>
                                <span>{formatCurrency(balanceSheet.current?.current_assets)}</span>
                            </div>
                            <div className="bs-row">
                                <span>Cash & Equivalents</span>
                                <span>{formatCurrency(balanceSheet.current?.cash)}</span>
                            </div>
                        </div>

                        <div className="bs-section">
                            <h4>Liabilities</h4>
                            <div className="bs-row">
                                <span>Total Liabilities</span>
                                <span>{formatCurrency(balanceSheet.current?.total_liabilities)}</span>
                            </div>
                            <div className="bs-row">
                                <span>Current Liabilities</span>
                                <span>{formatCurrency(balanceSheet.current?.current_liabilities)}</span>
                            </div>
                            <div className="bs-row">
                                <span>Total Debt</span>
                                <span>{formatCurrency(balanceSheet.current?.total_debt)}</span>
                            </div>
                        </div>

                        <div className="bs-section">
                            <h4>Equity</h4>
                            <div className="bs-row">
                                <span>Shareholders' Equity</span>
                                <span>{formatCurrency(balanceSheet.current?.total_equity)}</span>
                            </div>
                        </div>

                        <div className="bs-section ratios">
                            <h4>Key Ratios</h4>
                            <div className="bs-row">
                                <span>Current Ratio</span>
                                <span className={balanceSheet.ratios?.current_ratio >= 1 ? 'positive' : 'negative'}>
                                    {balanceSheet.ratios?.current_ratio?.toFixed(2)}x
                                </span>
                            </div>
                            <div className="bs-row">
                                <span>Debt to Equity</span>
                                <span className={balanceSheet.ratios?.debt_to_equity <= 1 ? 'positive' : 'negative'}>
                                    {balanceSheet.ratios?.debt_to_equity?.toFixed(2)}x
                                </span>
                            </div>
                            <div className="bs-row">
                                <span>Equity Ratio</span>
                                <span>{(balanceSheet.ratios?.equity_ratio * 100)?.toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                </Panel>
            )}

            {activeSection === 'peers' && peers?.peers && (
                <Panel title="Peer Comparison" icon={Users} iconColor="#10b981">
                    <div className="peer-info">
                        <span>Sector: <strong>{peers.sector}</strong></span>
                    </div>
                    <table className="fundamentals-table peer-table">
                        <thead>
                            <tr>
                                <th>Company</th>
                                <th>Price</th>
                                <th>P/E</th>
                                <th>P/B</th>
                                <th>ROE</th>
                                <th>D/E</th>
                                <th>Div Yield</th>
                            </tr>
                        </thead>
                        <tbody>
                            {peers.peers.map((peer, i) => (
                                <tr key={i} className={peer.is_target ? 'highlight' : ''}>
                                    <td>
                                        <strong>{peer.symbol}</strong>
                                        {peer.is_target && <span className="target-badge">Target</span>}
                                    </td>
                                    <td>₹{peer.price?.toLocaleString()}</td>
                                    <td>{peer.pe_ratio?.toFixed(1) || '-'}</td>
                                    <td>{peer.pb_ratio?.toFixed(1) || '-'}</td>
                                    <td className={peer.roe >= 15 ? 'positive' : ''}>{peer.roe?.toFixed(1)}%</td>
                                    <td className={peer.debt_to_equity <= 1 ? 'positive' : 'negative'}>
                                        {peer.debt_to_equity?.toFixed(2)}
                                    </td>
                                    <td>{peer.dividend_yield?.toFixed(2)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {peers.sector_averages && (
                        <div className="sector-averages">
                            <span>Sector Avg P/E: {peers.sector_averages.pe_ratio}</span>
                            <span>Sector Avg ROE: {peers.sector_averages.roe}%</span>
                        </div>
                    )}
                </Panel>
            )}
        </div>
    );
}

export default Fundamentals;
