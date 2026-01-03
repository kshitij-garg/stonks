import { TrendingUp, TrendingDown } from 'lucide-react';

function MarketOverview({ data, isLoading }) {
    if (isLoading) {
        return (
            <div className="market-indices">
                <div className="index-card">
                    <div className="loading-spinner" style={{ width: 20, height: 20 }} />
                </div>
                <div className="index-card">
                    <div className="loading-spinner" style={{ width: 20, height: 20 }} />
                </div>
            </div>
        );
    }

    if (!data) return null;

    const formatNumber = (num) => {
        return new Intl.NumberFormat('en-IN').format(Math.round(num));
    };

    return (
        <div className="market-indices" style={{ marginBottom: '1.5rem' }}>
            {data.nifty50 && (
                <div className="index-card glass-card">
                    <div className="index-name">NIFTY 50</div>
                    <div className="index-value">{formatNumber(data.nifty50.value)}</div>
                    <div className={`index-change ${data.nifty50.changePercent >= 0 ? 'positive' : 'negative'}`}>
                        {data.nifty50.changePercent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                        <span>{data.nifty50.change > 0 ? '+' : ''}{data.nifty50.change.toFixed(2)}</span>
                        <span>({data.nifty50.changePercent > 0 ? '+' : ''}{data.nifty50.changePercent.toFixed(2)}%)</span>
                    </div>
                </div>
            )}

            {data.sensex && (
                <div className="index-card glass-card">
                    <div className="index-name">SENSEX</div>
                    <div className="index-value">{formatNumber(data.sensex.value)}</div>
                    <div className={`index-change ${data.sensex.changePercent >= 0 ? 'positive' : 'negative'}`}>
                        {data.sensex.changePercent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                        <span>{data.sensex.change > 0 ? '+' : ''}{data.sensex.change.toFixed(2)}</span>
                        <span>({data.sensex.changePercent > 0 ? '+' : ''}{data.sensex.changePercent.toFixed(2)}%)</span>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MarketOverview;
