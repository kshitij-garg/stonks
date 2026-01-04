import { TrendingUp, TrendingDown, Coins, DollarSign, Fuel, Activity } from 'lucide-react';

function Commodities({ data, isLoading, error }) {
    if (isLoading) {
        return (
            <div className="commodities-panel glass-card">
                <div className="commodities-loading">Loading commodities...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="commodities-panel glass-card">
                <div className="commodities-error">Failed to load commodities</div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return null;
    }

    const getIcon = (symbol) => {
        switch (symbol) {
            case 'GOLD': return <Coins size={20} color="#ffd700" />;
            case 'SILVER': return <Coins size={20} color="#c0c0c0" />;
            case 'CRUDEOIL': return <Fuel size={20} color="#8b4513" />;
            default: return <Activity size={20} />;
        }
    };

    return (
        <div className="commodities-panel">
            <div className="commodities-header">
                <h3>
                    <DollarSign size={18} />
                    Commodities
                </h3>
            </div>
            <div className="commodities-grid">
                {data.map(commodity => (
                    <div key={commodity.symbol} className="commodity-card glass-card">
                        <div className="commodity-icon">
                            {getIcon(commodity.symbol)}
                        </div>
                        <div className="commodity-info">
                            <span className="commodity-name">{commodity.name}</span>
                            <span className="commodity-unit">{commodity.unit}</span>
                        </div>
                        <div className="commodity-price">
                            <span className="price">₹{commodity.price?.toLocaleString()}</span>
                            <span className={`change ${commodity.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                {commodity.change_percent >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                {commodity.change_percent >= 0 ? '+' : ''}{commodity.change_percent?.toFixed(2)}%
                            </span>
                        </div>
                        {commodity.returns && (
                            <div className="commodity-returns">
                                {commodity.returns['1W'] && (
                                    <span className={commodity.returns['1W'] >= 0 ? 'positive' : 'negative'}>
                                        1W: {commodity.returns['1W'] >= 0 ? '+' : ''}{commodity.returns['1W'].toFixed(1)}%
                                    </span>
                                )}
                                {commodity.returns['1M'] && (
                                    <span className={commodity.returns['1M'] >= 0 ? 'positive' : 'negative'}>
                                        1M: {commodity.returns['1M'] >= 0 ? '+' : ''}{commodity.returns['1M'].toFixed(1)}%
                                    </span>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Commodities;
