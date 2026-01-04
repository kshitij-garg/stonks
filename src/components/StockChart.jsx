import { useState, useMemo } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Area } from 'recharts';
import { TrendingUp, TrendingDown, BarChart2, Settings, ZoomIn, ZoomOut } from 'lucide-react';

function StockChart({ data, symbol, isLoading, error }) {
    const [showVolume, setShowVolume] = useState(true);
    const [showSMA, setShowSMA] = useState(true);
    const [showBB, setShowBB] = useState(false);
    const [zoomLevel, setZoomLevel] = useState(90); // Days to show

    const chartData = useMemo(() => {
        if (!data?.candles) return [];
        return data.candles.slice(-zoomLevel).map(candle => ({
            ...candle,
            date: candle.date?.split('T')[0] || candle.date,
            // Color based on open vs close
            fill: candle.close >= candle.open ? 'var(--accent-green)' : 'var(--accent-red)',
            // Calculate candle body
            bodyLow: Math.min(candle.open, candle.close),
            bodyHigh: Math.max(candle.open, candle.close),
        }));
    }, [data, zoomLevel]);

    if (isLoading) {
        return (
            <div className="chart-container glass-card">
                <div className="chart-loading">
                    <div className="loading-spinner" />
                    <span>Loading chart data...</span>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="chart-container glass-card">
                <div className="chart-error">Failed to load chart</div>
            </div>
        );
    }

    const latestPrice = chartData[chartData.length - 1]?.close || 0;
    const firstPrice = chartData[0]?.close || latestPrice;
    const priceChange = ((latestPrice - firstPrice) / firstPrice) * 100;

    const CustomTooltip = ({ active, payload }) => {
        if (!active || !payload?.[0]) return null;
        const d = payload[0].payload;
        return (
            <div className="chart-tooltip glass-card">
                <div className="tooltip-date">{d.date}</div>
                <div className="tooltip-row"><span>Open:</span> ₹{d.open?.toLocaleString()}</div>
                <div className="tooltip-row"><span>High:</span> ₹{d.high?.toLocaleString()}</div>
                <div className="tooltip-row"><span>Low:</span> ₹{d.low?.toLocaleString()}</div>
                <div className="tooltip-row"><span>Close:</span> ₹{d.close?.toLocaleString()}</div>
                {d.volume > 0 && <div className="tooltip-row"><span>Vol:</span> {(d.volume / 1e6).toFixed(2)}M</div>}
                {d.rsi && <div className="tooltip-row"><span>RSI:</span> {d.rsi}</div>}
            </div>
        );
    };

    return (
        <div className="chart-container glass-card">
            <div className="chart-header">
                <div className="chart-title">
                    <BarChart2 size={18} />
                    <span>{symbol} Price Chart</span>
                    <span className={`chart-change ${priceChange >= 0 ? 'positive' : 'negative'}`}>
                        {priceChange >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
                    </span>
                </div>
                <div className="chart-controls">
                    <button
                        className={`chart-btn ${showSMA ? 'active' : ''}`}
                        onClick={() => setShowSMA(!showSMA)}
                        title="Moving Averages"
                    >
                        SMA
                    </button>
                    <button
                        className={`chart-btn ${showBB ? 'active' : ''}`}
                        onClick={() => setShowBB(!showBB)}
                        title="Bollinger Bands"
                    >
                        BB
                    </button>
                    <button
                        className={`chart-btn ${showVolume ? 'active' : ''}`}
                        onClick={() => setShowVolume(!showVolume)}
                        title="Volume"
                    >
                        Vol
                    </button>
                    <div className="zoom-controls">
                        <button onClick={() => setZoomLevel(Math.min(zoomLevel + 30, 180))} title="Zoom Out">
                            <ZoomOut size={14} />
                        </button>
                        <span>{zoomLevel}d</span>
                        <button onClick={() => setZoomLevel(Math.max(zoomLevel - 30, 30))} title="Zoom In">
                            <ZoomIn size={14} />
                        </button>
                    </div>
                </div>
            </div>

            <div className="chart-area">
                <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <XAxis
                            dataKey="date"
                            tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                            tickFormatter={(val) => val?.slice(5) || val}
                            interval="preserveStartEnd"
                        />
                        <YAxis
                            domain={['auto', 'auto']}
                            tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                            tickFormatter={(val) => `₹${val.toLocaleString()}`}
                            width={70}
                        />
                        <Tooltip content={<CustomTooltip />} />

                        {/* Bollinger Bands */}
                        {showBB && (
                            <>
                                <Area
                                    type="monotone"
                                    dataKey="bb_upper"
                                    stroke="rgba(139, 92, 246, 0.3)"
                                    fill="rgba(139, 92, 246, 0.1)"
                                    strokeWidth={1}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="bb_lower"
                                    stroke="rgba(139, 92, 246, 0.3)"
                                    fill="transparent"
                                    strokeWidth={1}
                                />
                            </>
                        )}

                        {/* Price Line (simplified from candlestick) */}
                        <Line
                            type="monotone"
                            dataKey="close"
                            stroke="var(--accent-cyan)"
                            strokeWidth={2}
                            dot={false}
                            name="Price"
                        />

                        {/* Moving Averages */}
                        {showSMA && (
                            <>
                                <Line
                                    type="monotone"
                                    dataKey="sma20"
                                    stroke="#f59e0b"
                                    strokeWidth={1}
                                    dot={false}
                                    strokeDasharray="3 3"
                                    name="SMA 20"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="sma50"
                                    stroke="#ef4444"
                                    strokeWidth={1}
                                    dot={false}
                                    strokeDasharray="5 5"
                                    name="SMA 50"
                                />
                            </>
                        )}
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* Volume Chart */}
            {showVolume && (
                <div className="volume-chart">
                    <ResponsiveContainer width="100%" height={80}>
                        <ComposedChart data={chartData} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                            <XAxis dataKey="date" hide />
                            <YAxis
                                tick={{ fill: 'var(--text-muted)', fontSize: 9 }}
                                tickFormatter={(val) => `${(val / 1e6).toFixed(0)}M`}
                                width={70}
                            />
                            <Bar
                                dataKey="volume"
                                fill="rgba(0, 255, 255, 0.3)"
                                name="Volume"
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* RSI Chart */}
            {chartData[0]?.rsi && (
                <div className="rsi-chart">
                    <div className="indicator-label">RSI (14)</div>
                    <ResponsiveContainer width="100%" height={60}>
                        <ComposedChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                            <XAxis dataKey="date" hide />
                            <YAxis
                                domain={[0, 100]}
                                tick={{ fill: 'var(--text-muted)', fontSize: 9 }}
                                width={70}
                                ticks={[30, 50, 70]}
                            />
                            <ReferenceLine y={70} stroke="var(--accent-red)" strokeDasharray="3 3" />
                            <ReferenceLine y={30} stroke="var(--accent-green)" strokeDasharray="3 3" />
                            <Line
                                type="monotone"
                                dataKey="rsi"
                                stroke="var(--accent-purple)"
                                strokeWidth={1.5}
                                dot={false}
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
}

export default StockChart;
