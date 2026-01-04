import { TrendingUp, LayoutDashboard, Filter, Target, LineChart, Eye, Briefcase, GitCompare, RefreshCw, Calendar, Activity, BarChart2, Bell, Coins, FileText } from 'lucide-react';

function Header({ activeTab, setActiveTab, timeframe, setTimeframe, onRefresh }) {
    const mainTabs = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'recommendations', label: 'Recommendations', icon: Target },
        { id: 'screener', label: 'Screener', icon: Filter },
    ];

    const toolTabs = [
        { id: 'watchlist', label: 'Watchlist', icon: Eye },
        { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
        { id: 'compare', label: 'Compare', icon: GitCompare },
        { id: 'commodities', label: 'Commodities', icon: Coins },
        { id: 'alerts', label: 'Alerts', icon: Bell },
        { id: 'fundamentals', label: 'Fundamentals', icon: FileText },
        { id: 'backtesting', label: 'Backtest', icon: LineChart },
    ];

    return (
        <header className="header glass-card">
            <div className="header-brand">
                <div className="brand-icon">
                    <TrendingUp size={28} color="var(--accent-cyan)" />
                    <Activity size={16} color="var(--accent-green)" className="pulse-icon" />
                </div>
                <div>
                    <h1>Stonks by KG</h1>
                    <p>135+ Stocks • Gold • Silver • Crude Oil</p>
                </div>
            </div>

            <div className="header-controls">
                <div className="timeframe-selector">
                    <Calendar size={14} />
                    <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>
                </div>

                <nav className="header-nav">
                    <div className="nav-group main-nav">
                        {mainTabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <tab.icon size={14} />
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    <div className="nav-divider" />

                    <div className="nav-group tool-nav">
                        {toolTabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`tab tool-tab ${activeTab === tab.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                                title={tab.label}
                            >
                                <tab.icon size={14} />
                                <span className="tab-label-short">{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </nav>

                <button className="refresh-btn" onClick={onRefresh} title="Refresh Data">
                    <RefreshCw size={16} />
                </button>
            </div>
        </header>
    );
}

export default Header;
